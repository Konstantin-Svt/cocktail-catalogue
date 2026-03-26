import { useEffect, useMemo, useState } from 'react';
import { AlcoFilters } from '../AlcoFilters/AlcoFilters';
import { Catalog } from '../Catalog/Catalog';
import './MainPage.scss';
import { fetchCocktails } from '../../api/cocktailApi';

export interface FilterState {
    alcoholType: string[];
    alcoholLevel: string;
    price: [number, number];
    sweetnessLevel: string;
    vibe: string;
    search: string;
}

interface MainPageProps {
    searchQuery: string;
    activeFilters: FilterState;
    setActiveFilters: React.Dispatch<React.SetStateAction<FilterState>>;
    serverData: any;
    isLoading: boolean;
}

export const MainPage: React.FC<MainPageProps> = ({ searchQuery, activeFilters, setActiveFilters, serverData, isLoading }) => {

    useEffect(() => {
        if (searchQuery !== activeFilters.search) {
            setActiveFilters(prev => ({
                ...prev,
                search: searchQuery
            }));
        }
    }, [searchQuery, setActiveFilters]);
    
    const cocktails = useMemo(() => {
        if (!serverData) return [];
        return Array.isArray(serverData)
            ? serverData
            : (serverData.results || serverData.cocktails || []);
    }, [serverData]);

    if (isLoading && !serverData) {
        return <div className="loader">Завантаження коктейлів...</div>;
    }

    return (
        <div className="grid">
            <aside className="mainPage__filters">
                <AlcoFilters
                    onFilterChange={setActiveFilters}
                    filters={activeFilters}
                    summary={serverData}
                />
            </aside>

            <section className="mainPage__catalog">
                {isLoading && <div className="filtering-status">Оновлюємо список...</div>}

                <Catalog
                    activeFilters={activeFilters}
                    setFilters={setActiveFilters}
                    cocktails={cocktails}
                    ingredients={[]}
                    summary={serverData}
                />
            </section>
        </div>
    );
};