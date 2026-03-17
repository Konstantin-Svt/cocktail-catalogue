import { useEffect, useState } from 'react';
import { AlcoFilters } from '../AlcoFilters/AlcoFilters';
import { Catalog } from '../Catalog/Catalog';
import './MainPage.scss';
import { fetchIngredients, fetchVibes, fetchFilteredCocktails } from '../../api/cocktailApi';

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
}

export const MainPage: React.FC<MainPageProps> = ({ searchQuery }) => {
    const [activeFilters, setActiveFilters] = useState<FilterState>({
        alcoholType: [],
        alcoholLevel: '',
        price: [0, 180],
        sweetnessLevel: '',
        vibe: '',
        search: '',
    });

    const [cocktails, setCocktails] = useState<any[]>([]);
    const [fullCocktails, setFullCocktails] = useState<any[]>([]);
    const [ingredients, setIngredients] = useState<any[]>([]);
    const [vibes, setVibes] = useState<any[]>([]);
    const [initialLoading, setInitialLoading] = useState(true);
    const [isFiltering, setIsFiltering] = useState(false);     


    useEffect(() => {

        Promise.all([fetchIngredients(), fetchVibes(), fetchFilteredCocktails({})])
            .then(([iData, vData, cData]) => {
                setIngredients(iData);
                setVibes(vData);
                setFullCocktails(cData); 
                setInitialLoading(false);
            })
            .catch(err => {
                console.error("Помилка статики:", err);
                setInitialLoading(false);
            });
    }, []);


    useEffect(() => {
        setIsFiltering(true);
        fetchFilteredCocktails(activeFilters)
            .then(data => {
                setCocktails(data);
                setIsFiltering(false);
            })
            .catch(() => setIsFiltering(false));
    }, [activeFilters]);

    useEffect(() => {
        setActiveFilters(prev => ({
            ...prev,
            search: searchQuery
        }));
    }, [searchQuery]);
    
    if (initialLoading) return <div className="loader">Завантаження додатка...</div>;

    return (
        <div className="grid">
            <aside className="mainPage__filters">
                <AlcoFilters
                    onFilterChange={setActiveFilters}
                    filters={activeFilters}
                    cocktails={fullCocktails}
                    ingredients={ingredients}
                    setCocktails={setCocktails}
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
                        ingredients={ingredients}
                    />
                )}
            </section>
        </div>
    );
};