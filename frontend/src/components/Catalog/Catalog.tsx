import { CatalogCard } from '../CatalogCard/CatalogCard';
import './Catalog.scss';
import React, { useMemo } from 'react';
import { FilterState } from '../MainPage/MainPage';

interface Cocktail {
    id: number;
    name: string;
    description: string;
    average_price: string;
    alcohol_level: string;
    sweetness_level: string;
    preparation: string;
    preparation_time: number;
    image: string;
    vibes: any[]; // зазвичай масив об'єктів або ID
    ingredients: any[]; // зазвичай масив ID або об'єктів
}

interface Props {
    activeFilters: FilterState;
    setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
    cocktails: any[];
    ingredients: any[];
}

export const Catalog: React.FC<Props> = ({ activeFilters, setFilters, cocktails, ingredients }) => {

    const getIngredientsForCocktail = (cocktail: Cocktail): string[] => {
        // Перевірка на існування масиву інгредієнтів
        if (!cocktail.ingredients || !Array.isArray(cocktail.ingredients)) {
            return [];
        }

        if (typeof cocktail.ingredients[0] === 'string') {
            return cocktail.ingredients as unknown as string[];
        }

        return ingredients
            .filter(ing => cocktail.ingredients?.includes(ing.id))
            .map(ing => ing.name || "");
    };


    const filteredCocktails = useMemo(() => {

        if (!cocktails || !Array.isArray(cocktails)) return [];

        return cocktails.filter(cocktail => {
            const { alcoholType, alcoholLevel, price, sweetnessLevel, vibe } = activeFilters;

            const avgPrice = parseFloat(cocktail.average_price || "0");


            const matchesType = alcoholType.length === 0 ||
                alcoholType.some(type => {
                    const searchStr = type.toLowerCase();

         
                    const name = (cocktail.name || "").toLowerCase();
                    const description = (cocktail.description || "").toLowerCase();

                    const inBasicInfo = name.includes(searchStr) || description.includes(searchStr);

                    const cocktailIngredients = getIngredientsForCocktail(cocktail);
                    const inIngredients = cocktailIngredients.some(ingName =>
                        (ingName || "").toLowerCase().includes(searchStr)
                    );

                    return inBasicInfo || inIngredients;
                });


            const matchesLevel = !alcoholLevel ||
                (cocktail.alcohol_level || "").toLowerCase() === alcoholLevel.toLowerCase();


            const matchesPrice = avgPrice >= price[0] && avgPrice <= price[1];

            const matchesSweetness = !sweetnessLevel ||
                (cocktail.sweetness_level || "").toLowerCase() === sweetnessLevel.toLowerCase();

            const matchesVibe = !vibe || (cocktail.vibes && Array.isArray(cocktail.vibes) && cocktail.vibes.some((v: any) => {
                const vibeName = typeof v === 'string' ? v : v.name;
                return vibeName?.toLowerCase() === vibe.toLowerCase();
            }));

            return matchesType && matchesLevel && matchesPrice && matchesSweetness && matchesVibe;
        });
    }, [activeFilters, cocktails, ingredients]);

    const cocktailsCount = filteredCocktails.length;

    const removeType = (type: string) => {
        setFilters(prev => ({
            ...prev,
            alcoholType: prev.alcoholType.filter(t => t !== type)
        }));
    };

    const clearField = (key: keyof FilterState, defaultValue: any) => {
        setFilters(prev => ({ ...prev, [key]: defaultValue }));
    };

    return (
        <div className="catalog">
            <div className="catalog__header">
                <h1 className="catalog__title">{cocktailsCount} cocktails found</h1>

                <div className="catalog__controls">
                    <button className="catalog__sortBy">
                        <div className="catalog__img"></div>
                        <div className="catalog__sortBy-text">Sort by: Popular</div>
                        <div className="catalog__img2"></div>
                    </button>

                    <div className="catalog__chips">
                        {/* Типи алкоголю */}
                        {activeFilters.alcoholType.map(type => (
                            <div key={type} className="chip">
                                {type} <span className="chip__close" onClick={() => removeType(type)}>×</span>
                            </div>
                        ))}

                        {/* Міцність */}
                        {activeFilters.alcoholLevel && (
                            <div className="chip">
                                Level: {activeFilters.alcoholLevel}
                                <span className="chip__close" onClick={() => clearField('alcoholLevel', '')}>×</span>
                            </div>
                        )}

                        {/* Солодкість */}
                        {activeFilters.sweetnessLevel && (
                            <div className="chip">
                                {activeFilters.sweetnessLevel}
                                <span className="chip__close" onClick={() => clearField('sweetnessLevel', '')}>×</span>
                            </div>
                        )}

                        {/* Вайб */}
                        {activeFilters.vibe && (
                            <div className="chip">
                                {activeFilters.vibe}
                                <span className="chip__close" onClick={() => clearField('vibe', '')}>×</span>
                            </div>
                        )}

                        {/* Ціна */}
                        {(activeFilters.price[0] !== 0 || activeFilters.price[1] !== 180) && (
                            <div className="chip">
                                {activeFilters.price[0]}$ - {activeFilters.price[1]}$
                                <span className="chip__close" onClick={() => clearField('price', [0, 180])}>×</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="catalog__list">
                {filteredCocktails.length > 0 ? (
                    filteredCocktails.map((cocktail) => (
                        <CatalogCard
                            id={cocktail.id}
                            key={cocktail.id}
                            data={cocktail}
                            ingredients={getIngredientsForCocktail(cocktail)}
                        />
                    ))
                ) : (
                    <div className="catalog__no-results">
                        No cocktails found matching your filters.
                    </div>
                )}
            </div>
        </div>
    );
};