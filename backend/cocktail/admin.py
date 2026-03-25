from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from cocktail.models import (
    Cocktail,
    Vibe,
    Ingredient,
    CocktailIngredients,
    SimilarCocktails,
)

admin.site.unregister(Group)
admin.site.unregister(get_user_model())


@admin.register(Vibe)
class VibeAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "category", "unit")


class SimilarCocktailsInline(admin.TabularInline):
    model = SimilarCocktails
    fk_name = "from_cocktail"
    extra = 1
    autocomplete_fields = ("to_cocktail",)


class CocktailIngredientsInline(admin.TabularInline):
    model = CocktailIngredients
    fk_name = "cocktail"
    extra = 1
    autocomplete_fields = ("ingredient", "alternative_ingredient")


@admin.register(Cocktail)
class CocktailAdmin(admin.ModelAdmin):
    inlines = [CocktailIngredientsInline, SimilarCocktailsInline]
    search_fields = ["name", "description"]
    autocomplete_fields = ("ingredients", "vibes", "similar_cocktails")
    list_display = ("name", "alcohol_scale", "sweetness_scale")
