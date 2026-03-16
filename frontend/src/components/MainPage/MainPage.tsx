import { useState } from 'react';
import { AlcoFilters } from '../AlcoFilters/AlcoFilters';
import { Catalog } from '../Catalog/Catalog';
import './MainPage.scss';

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
    return (
        <div className="grid"> 
            <aside style={{ gridColumn: 'span 3' }}>
                <AlcoFilters onFilterChange={setActiveFilters} filters={activeFilters} />
            </aside>
            
            <section style={{ gridColumn: 'span 9' }}>
                <Catalog activeFilters={activeFilters} setFilters={setActiveFilters}/>
            </section>
        </div>
    )
}