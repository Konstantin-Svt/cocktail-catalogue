import React, { useMemo, useEffect } from 'react';
import { useGetFavoritesQuery } from '../../api/favoritesApi';
import { CatalogCard } from '../CatalogCard/CatalogCard';
import './FavoritesPage.scss';

interface FavoritesProps {
    searchQuery: string;
    onSearchClear?: (val: string) => void;
}
export const Favorites: React.FC<FavoritesProps> = ({ searchQuery, onSearchClear }) => {
    const { data: favorites = [], isLoading, isError } = useGetFavoritesQuery();
    const filteredFavorites = useMemo(() => {
        return favorites.filter(cocktail =>
            cocktail?.name?.toLowerCase().includes(searchQuery.toLowerCase())
        );
    }, [favorites, searchQuery]);
    useEffect(() => {
        return () => {
            if (onSearchClear) onSearchClear('');
        };
    }, [onSearchClear]);


    if (isLoading) return <div className="favorites-status">Loading favorites...</div>;
    if (isError) return <div className="favorites-status">Error loading favorites.</div>;

    return (
        <div className="favorites-page">
            <div className="favorites-page__container">
                <div className="favorites-page__controls">
                    <h1 className="favorites-page__title">Your Favorite Cocktails</h1>
                    <button className="sort-btn">
                        Sort by: <span>Popular ↓</span>
                    </button>
                </div>



                {filteredFavorites.length > 0 ? (
                    <div className="favorites-page__grid">
                        {filteredFavorites.map((cocktail) => (
                            <CatalogCard
                                key={cocktail.id}
                                id={cocktail.id}
                                data={cocktail}
                                ingredients={cocktail.ingredients || []}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="favorites-page__empty">
                        <p>{searchQuery ? "No cocktails match your search" : "Your favorites list is empty"}</p>
                    </div>
                )}
            </div>
        </div>
    );
};