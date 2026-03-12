import { AlcoFilters } from '../AlcoFilters/AlcoFilters';
import { Catalog } from '../Catalog/Catalog';
import './MainPage.scss';

export const MainPage = () => {
    return (
        <div className="grid"> 
            <aside style={{ gridColumn: 'span 3' }}>
                <AlcoFilters />
            </aside>
            
            <section style={{ gridColumn: 'span 9' }}>
                <Catalog />
            </section>
        </div>
    )
}