import { CatalogCard } from '../CatalogCard/CatalogCard';
import './Catalog.scss';
import React, { useMemo } from 'react';
import { FilterState } from '../MainPage/MainPage';
import { Link } from 'react-router-dom';

interface Props {
    activeFilters: FilterState;
    setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
    cocktails: any[];
    ingredients: any[];
    summary?: any;
}

export const Catalog: React.FC<Props> = ({ activeFilters, setFilters, cocktails, ingredients, summary }) => {

    const getIngredientsNames = (cocktail: any): string[] => {
        if (!cocktail.ingredients) return [];

        if (typeof cocktail.ingredients[0] === 'object') {
            return cocktail.ingredients.map((ing: any) => ing.name);
        }

        return cocktail.ingredients;
    };


    const displayCocktails = useMemo(() => {
        return Array.isArray(cocktails) ? cocktails : [];
    }, [cocktails]);

 
    const totalCount = summary?.general_count ?? displayCocktails.length;

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
                <h1 className="catalog__title">{totalCount} cocktails found</h1>

                <div className="catalog__controls">
                    <div className="catalog__buttons">
                        <button className="catalog__sortBy">
                            <span className="catalog__icon catalog__icon--pop1"></span>
                            <span className="catalog__sortBy-text">Sort</span>
                            <span className="catalog__icon catalog__icon--pop2"></span>
                        </button>

                        {/* Ця кнопка буде видима тільки на мобілці */}
                        <Link to="/filters" className="catalog__sortBy catalog__sortBy--mobile-only">
                            <span className="catalog__icon catalog__icon--filters"></span>
                            <span className="catalog__sortBy-text">Filters</span>
                        </Link>
                    </div>


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
                {displayCocktails.length > 0 ? (
                    displayCocktails.map((cocktail) => (
                        <CatalogCard
                            id={cocktail.id}
                            key={cocktail.id}
                            data={cocktail}
                            ingredients={getIngredientsNames(cocktail)}
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