import { useEffect, useState } from 'react';
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
}

export const MainPage: React.FC<MainPageProps> = ({ searchQuery, activeFilters, setActiveFilters }) => {

    const [cocktails, setCocktails] = useState<any[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [initialLoading, setInitialLoading] = useState(true);
    const [isFiltering, setIsFiltering] = useState(false);
    const [serverData, setServerData] = useState<any>(null);


    useEffect(() => {
        if (searchQuery !== activeFilters.search) {
            setActiveFilters(prev => ({
                ...prev,
                search: searchQuery
            }));
        }
    }, [searchQuery, activeFilters.search, setActiveFilters]);

    // Завантаження даних
    useEffect(() => {
        const loadData = async () => {
            setIsFiltering(true);
            try {
                const data = await fetchCocktails(activeFilters, currentPage);

                if (data && data.results) {
                    setCocktails(data.results);
                    setServerData(data);
                } else {
                    setCocktails([]);
                }
            } catch (err) {
                console.error("Fetch error:", err);
                setCocktails([]);
            } finally {
                setInitialLoading(false);
                setIsFiltering(false);
            }
        };

        loadData();
    }, [
        activeFilters.alcoholType,
        activeFilters.alcoholLevel,
        activeFilters.price,
        activeFilters.sweetnessLevel,
        activeFilters.vibe,
        activeFilters.search,
        currentPage
    ]);

    if (initialLoading) {
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
                {isFiltering ? (
                    <div className="filtering-status">Оновлюємо список...</div>
                ) : (
                    <Catalog
                            activeFilters={activeFilters}
                            setFilters={setActiveFilters}
                            cocktails={cocktails}
                            ingredients={[]}
                            summary={serverData}
                    />
                )}
            </section>
        </div>
    );
};