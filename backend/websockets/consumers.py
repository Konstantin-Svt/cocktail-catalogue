import asyncio
import json
from functools import wraps
from typing import Type

from httpx import AsyncClient, Timeout, Response, HTTPStatusError
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from cocktail.models import Cocktail, Vibe, Ingredient
from cocktail.serializers import AIFiltersSerializer

MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
HEADERS = {
    "content-type": "application/json",
    "x-goog-api-key": settings.GEMINI_API_KEY,
}


def ai_api_decorator(retries: int, exception: Type[Exception]):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            for i in range(retries):
                try:
                    res = await func(*args, **kwargs)
                    res.raise_for_status()
                    return res
                except exception as e:
                    print(e)
                    print(res.json())
                    await asyncio.sleep(2 * i + 1)
            else:
                await self.send(text_data=json.dumps({"message": "API Error"}))
                await self.close()
                raise Exception(f"External API Error for {retries} retries")
        return wrapper
    return decorator


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
            Ingredient.objects.filter(
                category__in=[
                    Ingredient.Category.ALCOHOL,
                    Ingredient.Category.MIXER,
                ]
            )[:40].values_list("name", flat=True)
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
        Cocktail.objects.with_levels()
        .prefetch_related("vibes")
        .filter(**conditions)
        .distinct()
        .values_list("id", "name")[:3]
    )
    filters_popped = False
    while len(result) == 0 and len(conditions) > 1:
        conditions.popitem()
        result = list(
            Cocktail.objects.with_levels()
            .prefetch_related("vibes")
            .filter(**conditions)
            .distinct()
            .values_list("id", "name")[:3]
        )
        filters_popped = True
    return {"filters_popped": filters_popped, "res": result}




class AIFiltersConsumer(AsyncWebsocketConsumer):
    async def serializer_exc_fallback(
        self, model_result: dict
    ) -> Response:
        response = await self.client.post(
            self,
            url=MODELS_URL,
            headers=HEADERS,
            json = {
                "model": "gemini-3.1-flash-lite-preview",
                "system_instruction": self.system_instructions,
                "input": f"""Your previous JSON result: 
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
        )
        return response

    async def gemini_response_parser(self, response: Response) -> dict | None:
        try:
            response_data = (
                response.json()
                .get("outputs")[1]
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
            raise e
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            await self.send(
                text_data=json.dumps(
                    {"message": "Model returned invalid JSON"}
                )
            )
            await self.close()
            raise e

    async def connect(self):
        await self.accept()
        self.client = AsyncClient(timeout=Timeout(120.0))
        self.client.post = ai_api_decorator(5, HTTPStatusError)(self.client.post)
        self.chat_history = []
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
        - At least 1 filter should be applied.
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
        No ```json``` segregation.
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
        user_query = {"role": "user", "content": text_data}

        if len(self.chat_history) >= 6:
            self.chat_history = self.chat_history[-4:]
        self.chat_history.append(user_query)

        response = await self.client.post(
            self,
            url=MODELS_URL,
            headers=HEADERS,
            json={
                "model": "gemini-3.1-flash-lite-preview",
                "system_instruction": self.system_instructions,
                "input": self.chat_history,
            },
        )
        response_data = await self.gemini_response_parser(response)
        print(response_data)

        if response_data.get("type") == "extra_query":
            await self.send(
                text_data=json.dumps({"message": response_data.get("res")})
            )
        else:
            serializer = AIFiltersSerializer(data=response_data.get("res"))
            if not serializer.is_valid():
                for retry in range(3):
                    response = await self.serializer_exc_fallback(response_data)
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
            "content": json.dumps(response_data),
        }
        self.chat_history.append(model_response)

    async def disconnect(self, code):
        await self.client.aclose()
