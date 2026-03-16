import './CatalogCard.scss';
import { Link } from 'react-router-dom';

interface Props {
    data: {
        name: string;
        average_price: string;
        image: string;
        description: string;
        alcohol_level: string;
    }
    id: number,
}

export const CatalogCard: React.FC<Props> = ({ data, id }) => {
    return (
        <article className="cocktail-card">
            <Link to={`/product/${id}`} className="cocktail-card__link">
            <div className="cocktail-card__image">
                <img src={data.image} alt={data.name} />
            </div>
            </Link>
            <div className="cocktail-card__content">
                <Link to={`/product/${id}`} className="cocktail-card__link">
                <h3 className="cocktail-card__name">{data.name}</h3>
                </Link>
                <p className="cocktail-card__description">{data.description}</p>
                <div className="cocktail-card__footer">
                    <span className="cocktail-card__price">${data.average_price}</span>
                    <span className="cocktail-card__level">{data.alcohol_level}</span>
                </div>
            </div>
        </article>
    );
}