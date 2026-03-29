from django import forms
from django.contrib import admin

from cocktail.models import (
    Cocktail,
    Vibe,
    Ingredient,
    CocktailIngredients,
    SimilarCocktails,
)


@admin.register(Vibe)
class VibeAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "category", "unit")


class CocktailIngredientsForm(forms.ModelForm):
    class Meta:
        model = CocktailIngredients
        fields = "__all__"

    def validate_unique(self):
        pass


class SimilarCocktailsForm(forms.ModelForm):
    class Meta:
        model = SimilarCocktails
        fields = "__all__"

    def validate_unique(self):
        pass


class SimilarCocktailsInline(admin.TabularInline):
    model = SimilarCocktails
    form = SimilarCocktailsForm
    fk_name = "from_cocktail"
    extra = 1
    autocomplete_fields = ("to_cocktail",)


class CocktailIngredientsInline(admin.TabularInline):
    model = CocktailIngredients
    form = CocktailIngredientsForm
    fk_name = "cocktail"
    extra = 1
    autocomplete_fields = ("ingredient", "alternative_ingredient")


@admin.register(Cocktail)
class CocktailAdmin(admin.ModelAdmin):
    inlines = [CocktailIngredientsInline,]
    search_fields = ["name", "description"]
    autocomplete_fields = ("ingredients", "vibes")
    list_display = ("name", "alcohol_scale", "sweetness_scale")
