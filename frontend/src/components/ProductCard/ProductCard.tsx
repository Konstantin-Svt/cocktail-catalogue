import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import './ProductCard.scss';
import { fetchCocktailById, sendAnalyticsEvent } from '../../api/cocktailApi';
import {CatalogCard} from '../CatalogCard/CatalogCard';
import { Comments } from './Comments/Comments';
import { favoritesApi } from '../../api/favoritesApi';

type Tab = 'ingredients' | 'preparation';

export const ProductCard: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [cocktail, setCocktail] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [servings, setServings] = useState(1);
    const [unit, setUnit] = useState<'ml' | 'oz' | 'cl'>('ml');
    const [isFirstRender, setIsFirstRender] = useState(true);
    const [activeTab, setActiveTab] = useState<Tab>('ingredients');
    const [addFavorite] = favoritesApi.useAddToFavoritesMutation();
    const [removeFavorite] = favoritesApi.useRemoveFromFavoritesMutation();

    const cocktailId = Number(id);
    const token = localStorage.getItem('access_token');
    const isAuthenticated = !!token;
    const { data: favoriteItems } = favoritesApi.useGetFavoritesQuery(undefined, {
        skip: !isAuthenticated,
    });

    const isFavorite = favoriteItems?.some((item: any) => item.id === cocktailId) || false;



    const handleFavoriteClick = async () => {
        if (!isAuthenticated) {
            alert("Please log in to save favorites");
            return;
        }

        try {
            if (isFavorite) {
                await removeFavorite({ cocktail_id: cocktailId }).unwrap();
            } else {
                await addFavorite({ cocktail_id: cocktailId }).unwrap();
            }
        } catch (error) {
            console.error("Failed to update favorites:", error);
        }
    };
    useEffect(() => {
        if (isFirstRender) {
            setIsFirstRender(false);
            return;
        }
        sendAnalyticsEvent({
            event_name: "servings_changed",
            servings_number: servings,
        });
    }, [servings]);

    const convertAmount = (amount: number, backendUnit: string) => {
        const totalAmount = amount * servings;
        const lowUnit = backendUnit?.toLowerCase();

        const fluidUnits = ['ml', 'oz', 'cl'];

        if (!fluidUnits.includes(lowUnit)) {
            return `${totalAmount} ${backendUnit}`;
        }


        switch (unit) {
            case 'oz':
                return `${(totalAmount * 0.0338).toFixed(1)} oz`;
            case 'cl':
                return `${(totalAmount / 10).toFixed(1)} cl`;
            default:
                return `${totalAmount} ml`;
        }
    };
    useEffect(() => {
        if (!id) return;

        const loadData = async () => {
            try {
                const data = await fetchCocktailById(id);
                setCocktail(data);
            } catch (err) {
                console.error("Failed to fetch cocktail:", err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [id]);

    if (loading) return <div className="loader">Завантаження...</div>;
    if (!cocktail) return <div className="error">Коктейль не знайдено</div>;

    const ingredients = cocktail.ingredients || [];
    const mainIngredients = ingredients.filter((ing: any) => ing.category !== 'garnish');

    const glass = ingredients
        .filter((ing: any) => ing.category === 'glass')
        .map((ing: any) => ing.name)
        .join(', ');

    const garnishIngredients = ingredients
        .filter((ing: any) => ing.category === 'garnish')
        .map((ing: any) => ing.name)
        .join(', ');

    const alternativeIngredients = ingredients
        .filter((ing: any) => ing.alternative)
        .map((ing: any) => `${ing.name} → ${ing.alternative}`)
        .join(', ');

    const calculateDrinks = (ingredients: any[]) => {

        const alcoholVolume = ingredients
            .filter(ing => ing.category === 'alcohol')
            .reduce((acc, ing) => acc + ing.amount, 0);
        return (alcoholVolume / 45).toFixed(1);
    };
    
    return (
        <div className="product-page">
            <div className="grid">
                <div className="product-page__back">
                    <Link to="/" className='product-page__back-text'>← Back to cocktails</Link>
                </div>
                <div className="product-page__cocktail">
                    <div className="cocktail__img"> 
                        <img src={cocktail.image} alt={cocktail.name} />
                    </div>
                    <div className="cocktail__info">
                        <div className="cocktail__nav">
                            <div className="cocktail__title">{cocktail.name}</div>
                            
                            <div
                                className={`cocktail__button cocktail__button--save ${isFavorite ? 'active' : ''}`}
                                onClick={handleFavoriteClick}
                                style={{ cursor: 'pointer' }}
                            >
                                {isFavorite ? (
                                    <span className='heart-icon heart-icon-checked'>

                                    </span>
                                ) : (
                                    <span className='heart-icon heart-icon-default'>

                                    </span>
                                )}
                            </div>
                            
                        </div>
                        <div className="cocktail__rates">
                            <div className="cocktail__rate">★ 4.8</div>
                            <div className="cocktail__rate">$ {Math.round(cocktail.average_price)}</div>
                            <div className="cocktail__rate">🕒 {cocktail.preparation_time || 5} min</div>
                        </div>
                        <div className="cocktail__description">
                            <h2 className='cocktail__description-title'>Description</h2>
                            <span className='cocktail__description-text'>{cocktail.description}</span>
                        </div>
                        <h2 className='cocktail__details-title'>Drink details</h2>
                        <div className="cocktail__details">
                            <div className="cocktail__detail"><span className='cocktail__text'>
                                {cocktail.ingredients ? calculateDrinks(cocktail.ingredients) : '0.0'}</span></div>
                            <div className="cocktail__detail"><span className='cocktail__text'>
                                {cocktail.alcohol_level}</span></div>
                        </div>
                    </div>
                </div>
                <div className="making__header">
                    <h2 className='making__title'>How to make</h2>
                    <div className="making__controls">
                        <div className="making__measure">
                            <button className={`making__size ${unit === 'oz' ? 'active' : ''}`} onClick={() => setUnit('oz')}>oz</button>
                            <button className={`making__size ${unit === 'ml' ? 'active' : ''}`} onClick={() => setUnit('ml')}>ml</button>
                            <button className={`making__size ${unit === 'cl' ? 'active' : ''}`} onClick={() => setUnit('cl')}>cl</button>
                        </div>
                        <div className="making__serves">
                            <button className='making__button' onClick={() => setServings(Math.max(1, servings - 1))}>-</button>
                            <span className="making__serves-text">{servings} serving</span>
                            <button className='making__button' onClick={() => setServings(servings + 1)}>+</button>
                        </div>
                    </div>
                </div>

                {/* 2. Блок самої картки (Інгредієнти + Приготування) */}
                <div className="making__card">
                    {/* Таби відображатимуться лише на мобілці через CSS */}
                    <div className="making__mobile-tabs">
                        <button
                            className={`making__tab ${activeTab === 'ingredients' ? 'active' : ''}`}
                            onClick={() => setActiveTab('ingredients')}
                        >
                            Ingredients
                        </button>
                        <button
                            className={`making__tab ${activeTab === 'preparation' ? 'active' : ''}`}
                            onClick={() => setActiveTab('preparation')}
                        >
                            Preparation
                        </button>
                    </div>

                    {/* Додаємо динамічні класи залежно від activeTab */}
                    <div className={`making__page making__ingredients ${activeTab === 'ingredients' ? 'is-active' : 'is-hidden'}`}>
                        <h3 className="making__subtitle">Ingredients</h3>
                        <ul className="ingredients__list">
                            {mainIngredients.map((ing: any) => (
                                <li key={ing.id} className="ingredients__item">
                                    <div className="ingredients__name-wrapper">
                                        <span className={`ingredients__dot ${ing.category === 'alcohol' ? 'ingredients__dot--active' : ''}`}></span>
                                        <span className="ingredients__name">{ing.name}</span>
                                    </div>
                                    <span className="ingredients__amount">
                                        {ing.optional ? 'optional' : convertAmount(ing.amount, ing.unit)}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className={`making__page making__preparation ${activeTab === 'preparation' ? 'is-active' : 'is-hidden'}`}>
                        <h3 className="making__subtitle">Preparation</h3>
                        <div className="preparation__list">
                            {cocktail.preparation.split('.').filter((s: string) => s.trim()).map((step: string, index: number) => (
                                <div key={index} className="preparation__step">
                                    <span className="step__number">{index + 1}</span>
                                    <p className="step__text">{step.trim()}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
                <div className="making__extra">
                    <div className="extra-card">
                        <span className="extra-card__label">Glass</span>
                        <div className="extra-card__content">
                            <span className="extra-card__value">{glass || cocktail.glass_type || 'Nothing'}</span>
                        </div>
                    </div>

                    <div className="extra-card">
                        <span className="extra-card__label">Garnish</span>
                        <div className="extra-card__content">
                            <span className="extra-card__value">{garnishIngredients || cocktail.garnish || 'Nothing'}</span>
                        </div>
                    </div>

                    <div className="extra-card">
                        <span className="extra-card__label">Alternative ingredients</span>
                        <div className="extra-card__content">
                            <span className="extra-card__value">{alternativeIngredients || cocktail.alternative || 'Nothing'}</span>
                        </div>
                    </div>
                </div>
                <div className="guide">
                    <h2 className="guide__title">Strength & taste guide:</h2>
                    <div className="guide__container">

                        {/* Шкала міцності (Strength) */}
                        <div className="guide__item">
                            <div className="guide__track">
                                {[...Array(10)].map((_, i) => (
                                    <div
                                        key={i}
                                        className={`guide__segment ${i < (cocktail.alcohol_scale || 7) ? 'active' : ''}`}
                                    />
                                ))}
                            </div>
                            <div className="guide__labels">
                                <span className="guide__label">No alcohol</span>
                                <span className="guide__label">Medium</span>
                                <span className="guide__label">Boozy</span>
                            </div>
                        </div>

                        {/* Шкала смаку (Taste) */}
                        <div className="guide__item">
                            <div className="guide__track">
                                {[...Array(10)].map((_, i) => (
                                    <div
                                        key={i}
                                        className={`guide__segment ${i < (cocktail.sweetness_scale || 8) ? 'active' : ''}`}
                                    />
                                ))}
                            </div>
                            <div className="guide__labels">
                                <span className="guide__label">Dry/sour</span>
                                <span className="guide__label">Medium</span>
                                <span className="guide__label">Sweet</span>
                            </div>
                        </div>

                    </div>
                </div>
                {cocktail.similar_cocktails && cocktail.similar_cocktails.length > 0 && (
                    <div className="similar">
                        <h2 className="similar__title">Similar cocktails:</h2>
                        <div className="similar__grid">
                            {cocktail.similar_cocktails.map((similar: any) => (
                                <div key={similar.id} className="similar__item">
                                    <CatalogCard
                                        id={similar.id}
                                        data={similar}
                                        ingredients={similar.ingredients?.map((ing: any) =>
                                            typeof ing === 'string' ? ing : ing.name
                                        ) || []}
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
            <div className="review">
                <Comments
                    cocktailId={id!}
                    initialComments={cocktail.reviews || []}
                />
            </div>
        </div>
    )
};