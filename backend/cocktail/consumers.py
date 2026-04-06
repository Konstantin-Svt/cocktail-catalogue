import json

import httpx
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from cocktail.models import Cocktail, Vibe, Ingredient

client = httpx.AsyncClient()


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


class AIFiltersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.chat_history = []
        self.client = client
        self.filters = await get_filters()
        self.system_instructions = f"""
        You are a barman AI assistant.

        Your job is to convert user messages into structured filters.
        
        Rules:
        - Filters are combined using AND logic.
        - Each filter has only one value (or null if not applicable).
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
        prompt = {"user": text_data}
