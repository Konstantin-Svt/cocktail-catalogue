import json

from httpx import AsyncClient
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from cocktail.models import Cocktail, Vibe, Ingredient
from cocktail.serializers import AIFiltersSerializer
from cocktail.views import CocktailViewSet

CLIENT = AsyncClient()


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


async def serializer_exc_fallback(a_client: AsyncClient, model_result: dict):
    async with a_client as client:
        response = await client.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent",
            headers={
                "content-type": "application/json",
                "x-goog-api-key": settings.GEMINI_API_KEY,
            },
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
    return response.json()


@database_sync_to_async
def get_cocktails(filters: dict) -> dict:
    conditions = {
        "alcohol_level": filters["alcohol_level"],
        "ingredients__name__in": filters["ingredients"],
        "sweetness_level": filters["sweetness_level"],
        "vibes__name__in": [filters["vibe"]],
    }
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
    return {"filters_popped": filters_popped, "result": result}


class AIFiltersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.chat_history = []
        self.client = CLIENT
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
          "content": {{
            "alcohol_level": string or null,
            "sweetness_level": string or null,
            "vibe": string or null,
            "ingredients": [string] or null,
          }}
        }}
        
        If more info is needed (max 2 times):
        {{
          "type": "extra_query",
          "content": "Your question to user (max 200 chars)"
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

        async with self.client as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent",
                headers={
                    "content-type": "application/json",
                    "x-goog-api-key": settings.GEMINI_API_KEY,
                },
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
        response_data = response.json()

        if response_data.get("type") == "extra_query":
            await self.send(
                text_data=json.dumps({"message": response_data.get("content")})
            )
        else:
            serializer = AIFiltersSerializer(data=response_data.get("content"))
            if not serializer.is_valid():
                for retry in range(3):
                    response_data = await serializer_exc_fallback(
                        self.client, response_data
                    )
                    serializer = AIFiltersSerializer(
                        data=response_data.get("content")
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
            intro = (
                (
                    "I had to discard some filters because initially there were 0 results."
                    "But after that, here what I found for you:\n"
                )
                if db_results["filters_popped"] is True
                else "Here, you may like these:\n"
            )
            message = intro + "\n".join(
                [
                    f"- {name}: {settings.FRONTEND_BASE_URL}/#/product/{cid}"
                    for cid, name in db_results["result"]
                ]
            )

        model_response = {"role": "model", "parts": [{"text": response_data}]}
        self.chat_history.append(model_response)
        print(response_data)
