import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from google import genai

from cocktail.models import Cocktail, Vibe, Ingredient

CLIENT = genai.Client()


@database_sync_to_async
def get_filters() -> dict:
    return {
        "vibes": list(Vibe.objects.values_list("name", flat=True)),
        "ingredients": list(
            Ingredient.objects.filter(category=Ingredient.Category.ALCOHOL)[
                :20
            ].values_list("name", flat=True)
        ),
        "alcohol_level": [
            alcohol.name for alcohol in Cocktail.ALCOHOL_SCALE_MAP
        ],
        "sweetness_level": [
            sweetness.name for sweetness in Cocktail.SWEETNESS_SCALE_MAP
        ],
    }


class AIFiltersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.chat_history = []
        self.client = CLIENT
        self.filters = get_filters()
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
