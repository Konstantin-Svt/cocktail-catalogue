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
}

export const MainPage = () => {
    const [activeFilters, setActiveFilters] = useState<FilterState>({
        alcoholType: [],
        alcoholLevel: '',
        price: [0, 180],
        sweetnessLevel: '',
        vibe: '',
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


    if (initialLoading) return <div className="loader">Завантаження додатка...</div>;

    return (
        <div className="grid">
            <aside style={{ gridColumn: 'span 3' }}>
                <AlcoFilters
                    onFilterChange={setActiveFilters}
                    filters={activeFilters}
                    cocktails={fullCocktails}
                    ingredients={ingredients}
                    setCocktails={setCocktails}
                />
            </aside>

            <section style={{ gridColumn: 'span 9' }}>
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