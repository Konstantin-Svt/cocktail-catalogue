import json

from httpx import AsyncClient, Timeout, Response, HTTPStatusError
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from cocktail.models import Cocktail, Vibe, Ingredient
from cocktail.serializers import AIFiltersSerializer
from cocktail.views import CocktailViewSet

MODEL_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent"
HEADERS = {
    "content-type": "application/json",
    "x-goog-api-key": settings.GEMINI_API_KEY,
}


@database_sync_to_async
def get_filters():
    return {
        "alcohol_level": [
            alcohol.name for alcohol in Cocktail.ALCOHOL_SCALE_MAP
        ],
        "sweetness_level": [
            sweetness.name for sweetness in Cocktail.SWEETNESS_SCALE_MAP
        ],
        "vibe": list(Vibe.objects.values_list("name", flat=True)),
        "ingredients": list(
            Ingredient.objects.filter(category=Ingredient.Category.ALCOHOL)[
                :20
            ].values_list("name", flat=True)
        ),
    }


@database_sync_to_async
def get_cocktails(filters: dict) -> dict:
    conditions = {
        "alcohol_level": filters["alcohol_level"],
        "ingredients__name__in": filters["ingredients"],
        "sweetness_level": filters["sweetness_level"],
        "vibes__name__in": [filters["vibe"]] if filters["vibe"] else None,
    }
    copy = conditions.copy()
    for condition in copy:
        if conditions[condition] is None:
            del conditions[condition]

    result = list(
        CocktailViewSet.queryset.filter(**conditions)
        .distinct()
        .values_list("id", "name")[:3]
    )
    filters_popped = False
    while len(result) == 0 and len(conditions) > 1:
        conditions.popitem()
        result = list(
            CocktailViewSet.queryset.filter(**conditions)
            .distinct()
            .values_list("id", "name")[:3]
        )
        filters_popped = True
    return {"filters_popped": filters_popped, "res": result}


async def serializer_exc_fallback(
    a_client: AsyncClient, model_result: dict
) -> Response:
    response = await a_client.post(
        url=MODEL_URL,
        headers=HEADERS,
        json={
            "contents": {
                "role": "server",
                "parts": [
                    {
                        "text": f"""Your previous JSON result: 
                                {json.dumps(model_result, indent=2, ensure_ascii=False)}
                                
                                It should have looked like this:
                                {{
                                  "type": "result",
                                  "content": {{
                                    "alcohol_level": string or null,
                                    "sweetness_level": string or null,
                                    "vibe": string or null,
                                    "ingredients": [string] or null,
                                  }}
                                }}
                                
                                Fix it and return ONLY valid JSON.
                                No explanations.
                                No additional text.
                                """
                    }
                ],
            }
        },
    )
    return response


class AIFiltersConsumer(AsyncWebsocketConsumer):
    async def gemini_response_parser(self, response: Response) -> dict | None:
        try:
            response.raise_for_status()
            response_data = (
                response.json()
                .get("candidates")[0]
                .get("content")
                .get("parts")[0]
                .get("text")
            )
            response_data = json.loads(response_data)
            r_type = response_data.get("type")
            res = response_data.get("res")
            if r_type == "result":
                if not isinstance(res, dict):
                    raise TypeError
            elif r_type == "extra_query":
                if not isinstance(res, str):
                    raise TypeError

            return response_data
        except HTTPStatusError as e:
            print("HTTP API Error:", e)
            await self.send(text_data=json.dumps({"message": "API Error"}))
            await self.close()
        except (KeyError, IndexError, TypeError) as e:
            print("Structure error:", e)
            await self.send(
                text_data=json.dumps(
                    {
                        "message": "Error. Invalid response structure of the model."
                    }
                )
            )
            await self.close()
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            await self.send(
                text_data=json.dumps(
                    {"message": "Model returned invalid JSON"}
                )
            )
            await self.close()

    async def connect(self):
        await self.accept()
        self.chat_history = []
        self.client = AsyncClient(timeout=Timeout(120.0))
        self.filters = await get_filters()
        self.system_instructions = f"""
        You are a barman AI assistant.

        Your job is to convert user messages into structured filters.
        
        Rules:
        - Filters are combined using AND logic.
        - Each filter has only one value (or null if not applicable - filter is skipped then).
        - "ingredients" can contain multiple values (OR logic).
        - Use ONLY values from provided filters.
        - Do NOT invent new values.
        - If unsure — return null.

        Filters are:
        {json.dumps(self.filters, indent=2, ensure_ascii=False)}
        
        Response format:

        If you can determine filters:
        {{
          "type": "result",
          "res": {{
            "alcohol_level": string or null,
            "sweetness_level": string or null,
            "vibe": string or null,
            "ingredients": [string] or null,
          }}
        }}
        
        If more info is needed (max 2 times per one filters result):
        {{
          "type": "extra_query",
          "res": "Your question to user (max 200 chars)"
        }}
        Return ONLY valid JSON.
        No explanations.
        No additional text.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "message": "Hello, I am AI Assistant. I can help you to "
                    "choose cocktails that fit your description. "
                    "Just describe what's on your mind."
                }
            )
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data = json.loads(text_data).get("message")
        if len(text_data) > 500:
            text_data = text_data[:500]
        user_query = {"role": "user", "parts": [{"text": text_data}]}

        if len(self.chat_history) >= 6:
            self.chat_history = self.chat_history[-4:]
        self.chat_history.append(user_query)

        response = await self.client.post(
            url=MODEL_URL,
            headers=HEADERS,
            json={
                "system_instruction": {
                    "parts": [
                        {
                            "text": self.system_instructions,
                        }
                    ]
                },
                "contents": self.chat_history,
            },
        )
        response_data = await self.gemini_response_parser(response)

        if response_data.get("type") == "extra_query":
            await self.send(
                text_data=json.dumps({"message": response_data.get("res")})
            )
        else:
            serializer = AIFiltersSerializer(data=response_data.get("res"))
            if not serializer.is_valid():
                for retry in range(3):
                    response = await serializer_exc_fallback(
                        self.client, response_data
                    )
                    response_data = await self.gemini_response_parser(response)
                    serializer = AIFiltersSerializer(
                        data=response_data.get("res")
                    )
                    if serializer.is_valid():
                        break
                else:
                    await self.send(
                        text_data=json.dumps(
                            {
                                "message": "Error. Something went wrong.",
                            }
                        )
                    )
                    await self.close()

            db_results = await get_cocktails(serializer.data)
            if db_results["res"]:
                intro = (
                    (
                        "I had to discard some filters because initially there were 0 results."
                        "But after that, here what I found for you:\n"
                    )
                    if db_results["filters_popped"] is True
                    else "Here, you may like these:\n"
                )
                message = (
                    intro
                    + "".join(
                        [
                            f"- {name}: {settings.FRONTEND_BASE_URL}/product/{cid} \n"
                            for cid, name in db_results["res"]
                        ]
                    )
                    + "If you want more, ask again!"
                )
            else:
                message = "Sorry, I couldn't find any results for you. Maybe you want something else?"

            await self.send(text_data=json.dumps({"message": message}))

        model_response = {
            "role": "model",
            "parts": [{"text": json.dumps(response_data)}],
        }
        self.chat_history.append(model_response)

    async def disconnect(self, code):
        await self.client.aclose()
