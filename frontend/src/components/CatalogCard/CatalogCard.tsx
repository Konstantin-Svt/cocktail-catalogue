import './CatalogCard.scss';
import { Link } from 'react-router-dom';


interface CocktailData {
    id: number;
    name: string;
    description: string;
    average_price: string;
    alcohol_level: string;
    sweetness_level: string;
    image: string;
    preparation_time: number;
}

interface Props {
    data: CocktailData;
    id: number,
    ingredients: string[];
}

export const CatalogCard: React.FC<Props> = ({ data, ingredients, id }) => {

    const price = Math.round(Number(data.average_price));
    const getAlcoholStatusClass = (levelStr: string) => {

        const level = levelStr;

        if (level === 'non-alcoholic') return 'dot--gray';
        if (level === 'low') return 'dot--green';
        if (level === 'medium') return 'dot--yellow';
        return 'dot--red';
    };
    return (
        <article className="cocktail-card">
            <Link to={`/product/${id}`} className="cocktail-card__link">
                <div className="cocktail-card__image">
                    <img src={data.image} alt={data.name} className="cocktail-card__image-img" />
                </div>
            </Link>
            <div className="cocktail-card__content">
                <div className="cocktail-card__header">
                    <Link to={`/product/${id}`} className="cocktail-card__link">
                        <h3 className="cocktail-card__name">{data.name}</h3>
                    </Link>
                    <div className="cocktail-card__rating">
                        <span className="star">★</span> 4.6
                    </div>
                </div>
                <div className="cocktail-card__ingredients">
                    {ingredients.map((ing, index) => (
                        <span key={index} className="cocktail-card__tag">
                            {ing}
                        </span>
                    ))}
                </div>
                <div className="cocktail-card__footer">
                    <div className="cocktail-card__info">
                        <span className="icon">🕒</span>
                        <span className="text">{data.preparation_time} min</span>
                    </div>

                    <div className="divider"></div>

                    <div className="cocktail-card__info">
                        <span className={`dot ${getAlcoholStatusClass(data.alcohol_level)}`}></span>
                        <span className="text">{data.alcohol_level}</span>
                    </div>

                    <div className="divider"></div>

                    <div className="cocktail-card__info">
                        <span className="icon">$</span>
                        <span className="text price">{price}</span>
                    </div>
                </div>
            </div>
        </article>
    );
}