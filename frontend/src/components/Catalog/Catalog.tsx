import { CatalogCard } from '../CatalogCard/CatalogCard';
import './Catalog.scss';

export const Catalog = () => {
    return (
        <div className="catalog">
            <div className="catalog__title">
                <h1>140 cocktails found</h1>
            </div>
            <div className="catalog__info">
               <div className="catalog__text">
                    This website is intended for individuals who are 18 years of age or older.
                    It contains information related to cocktails and alcoholic beverages.
                    Our platform helps you discover, choose, and prepare cocktails that match your taste, mood, 
                    and preferences. Here you can explore ingredients, find step‑by‑step recipes, and select portion sizes that suit your needs.
               </div>
                    <button className='catalog__button'></button>
            </div>
            <CatalogCard />
        </div>
    )
}