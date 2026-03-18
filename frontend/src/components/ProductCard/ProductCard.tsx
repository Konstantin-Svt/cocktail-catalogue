import React from 'react';
import { useParams, Link } from 'react-router-dom';
import data from '../../../../backend/fixtures/data.json';
import './ProductCard.scss';

interface CocktailItem {
    pk: number;
    model: string;
    fields: {
        name: string;
        average_price: string;
        image: string;
        description: string;
        alcohol_level: string;
    };
}

export const ProductCard: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const cocktails = data as unknown as CocktailItem[];
    const cocktail = cocktails.find(item => item.pk === Number(id));

    if (!cocktail) return <div className="error">Cocktail not found</div>;

    const { name, image, description, average_price, alcohol_level } = cocktail.fields;

    return (
        <div className="product-card">
            <div className="container">
                <Link to="/" className="product-card__back">
                    ← Back to cocktails
                </Link>

                <div className="product-card__main">
                    <div className="product-card__image-block">
                        <img src={image} alt={name} className="product-card__img" />
                    </div>

                    <div className="product-card__info-block">
                        <h1 className="product-card__title">{name}</h1>

                        <div className="product-card__meta">
                            <span className="rating">⭐ 4.8</span>
                            <span className="price">${average_price}</span>
                            <span className="time">⏱ 5 min</span>
                        </div>

                        <div className="product-card__section">
                            <h3>Description</h3>
                            <p>{description}</p>
                        </div>

                        <div className="product-card__section">
                            <h3>Drink details</h3>
                            <div className="product-card__details-grid">
                                <div className="detail-box">
                                    <span className="value">168</span>
                                    <span className="label">kcal</span>
                                </div>
                                <div className="detail-box">
                                    <span className="value">1.4</span>
                                    <span className="label">drinks</span>
                                </div>
                                <div className="detail-box">
                                    <span className="value">{alcohol_level}</span>
                                    <span className="label">alc./vol</span>
                                </div>
                            </div>
                        </div>

                        <div className="product-card__section">
                            <h3>Allergens</h3>
                            <p>None</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};