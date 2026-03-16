import { CatalogCard } from '../CatalogCard/CatalogCard';
import './Catalog.scss';
import data from '../../../../backend/fixtures/data.json';
import React from 'react';
import { FilterState } from '../MainPage/MainPage';

interface CocktailItem {
    pk: number;
    model: string;
    fields: {
        name: string;
        average_price: string;
        image: string;
        description: string;
        alcohol_level: string;
    };
}

interface Props {
    activeFilters: FilterState;
    setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
}

export const Catalog: React.FC<Props> = ({ activeFilters, setFilters }) => {
    // Базовий масив коктейлів
    const allCocktails = data.filter(item => item.model === 'cocktail.cocktail') as unknown as CocktailItem[];

    // Логіка фільтрації
    const filteredCocktails = allCocktails.filter(cocktail => {
        const { alcoholType, alcoholLevel, price, sweetnessLevel, vibe } = activeFilters;
        const fields = cocktail.fields;
        const avgPrice = parseFloat(fields.average_price);

        // Текст для пошуку (назва + опис) для перевірки солодкості та вайбу
        const searchableText = `${fields.name} ${fields.description}`.toLowerCase();

        const matchesType = alcoholType.length === 0 ||
            alcoholType.some(type =>
                fields.description.toLowerCase().includes(type.toLowerCase()) ||
                fields.name.toLowerCase().includes(type.toLowerCase())
            );

        const matchesLevel = !alcoholLevel || fields.alcohol_level === alcoholLevel;

        const matchesPrice = avgPrice >= price[0] && avgPrice <= price[1];

        // Фільтр за солодкістю (шукаємо входження слова в описі)
        const matchesSweetness = !sweetnessLevel || searchableText.includes(sweetnessLevel.toLowerCase());

        // Фільтр за вайбом
        const matchesVibe = !vibe || searchableText.includes(vibe.toLowerCase());

        return matchesType && matchesLevel && matchesPrice && matchesSweetness && matchesVibe;
    });

    const cocktailsCount = filteredCocktails.length;

    // Функції видалення фільтрів
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
                            id={cocktail.pk}
                            key={cocktail.pk}
                            data={cocktail.fields}
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