from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cocktail.views import (
    CocktailViewSet,
    VibeViewSet,
    IngredientViewSet,
)

router = DefaultRouter()
router.register("cocktails", CocktailViewSet)
router.register("vibes", VibeViewSet)
router.register("ingredients", IngredientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
app_name = "cocktail"
