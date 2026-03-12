
import './CatalogCard.scss';

export const CatalogCard = () => {
    const cocktails = [
        { id: 1, name: 'Mojito', ingredients: 'White rum, lime, mint, sugar, soda water', time: '5 min', level: 'Easy' },
        { id: 2, name: 'Margarita', ingredients: 'Tequila, lime juice, triple sec', time: '5 min', level: 'Easy' },
        { id: 3, name: 'Classic Margarita', ingredients: 'White rum, coconut cream, pineapple juice', time: '10 min', level: 'Easy' },
    ];
    return (
        <div className="catalog">
            <div className="catalog__list">
                {cocktails.map(cocktail => (
                    <article key={cocktail.id} className="cocktail-card">
                        <div className="cocktail-card__image"></div>
                        <div className="cocktail-card__content">
                            <h3 className="cocktail-card__name">{cocktail.name}</h3>
                            <p className="cocktail-card__ingredients">{cocktail.ingredients}</p>
                            <div className="cocktail-card__footer">
                                <span className="cocktail-card__time">{cocktail.time}</span>
                                <span className="cocktail-card__level">{cocktail.level}</span>
                            </div>
                        </div>
                    </article>
                ))}
            </div>
        </div>
    );
}