from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from cocktail.models import (
    Cocktail,
    Tag,
    Ingredient,
    CocktailIngredients,
)

admin.site.unregister(Group)
admin.site.unregister(get_user_model())

admin.site.register(Tag)
admin.site.register(Ingredient)


class CocktailIngredientsInline(admin.TabularInline):
    model = CocktailIngredients
    fk_name = "cocktail"
    extra = 1


@admin.register(Cocktail)
class CocktailAdmin(admin.ModelAdmin):
    inlines = [CocktailIngredientsInline]
