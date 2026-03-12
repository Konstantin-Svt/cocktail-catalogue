import './AlcoFilters.scss';

export const AlcoFilters = () => {
    const alcoholTypes = [
        { name: 'Vodka', count: 12 },
        { name: 'Rum', count: 43 },
        { name: 'Gin', count: 21 },
        { name: 'Tequila', count: 23 },
        { name: 'Whiskey', count: 43 },
        { name: 'Liqueur', count: 54 },
        { name: 'Non-alcoholic', count: 12 },
    ];
    const alcoholLevels = [
        { name: 'Low', count: 23 },
        { name: 'Medium', count: 58 },
        { name: 'Strong', count: 32 },
    ];
    const sweetnessLevels = [
        { name: 'Dry', count: 16 },
        { name: 'Medium', count: 21 },
        { name: 'Sweet', count: 46 },
    ];
    const priceRanges = [
        { name: 'Low', count: 21 },
        { name: 'Medium', count: 34 },
        { name: 'High', count: 12 },
    ];
    const vibeTypes = [
        { name: 'Party', count: 12 },
        { name: 'Romantic', count: 21 },
        { name: 'Summer', count: 43 },
        { name: 'Tropical', count: 23 },
        { name: 'Classic', count: 12 },
    ];
    return (
        <div className="alcoFilters">
            <div className="alcoFilters__sections">
                <div className="alcoFilters__section">
                    <div className="section__right">Your Filters</div>
                    <div className="section__left">
                        <span className="reset__icon"></span> 
                        <a href="" className='reset__text'>Reset Filters</a>
                    </div>
                </div>
                <div className="alcoFilters__section">
                    <div className="alcoFilters__section-type">
                        <div className="type__title">
                            Alcohol Type
                        </div>
                        <div className="type__filters">
                            {alcoholTypes.map((type) => (
                                <label key={type.name} className="filter-item">
                                    <div className="filter-item__left">
                                        <input type="checkbox" className="filter-item__checkbox" />
                                        <span className="filter-item__custom"></span>
                                        <span className="filter-item__name">{type.name}</span>
                                    </div>
                                    <span className="filter-item__quantity">{type.count}</span>
                                </label>
                            ))}
                        </div>
                    </div>
                </div>
                <div className="alcoFilters__section">
                    <h3 className="filter-title">Alcohol Level</h3>
                    <div className="type__filters">
                        {alcoholLevels.map((level) => (
                            <label key={level.name} className="filter-item">
                                <div className="filter-item__left">
                                    <input type="radio" name="alcohol-level" className="filter-item__radio" />
                                    <span className="filter-item__custom-radio"></span>
                                    <span className="filter-item__name">{level.name}</span>
                                </div>
                                <span className="filter-item__quantity">{level.count}</span>
                            </label>
                        ))}
                    </div>
                </div>
                <div className="alcoFilters__section">
                    <h3 className="filter-title">Sweetness Level</h3>
                    <div className="type__filters">
                        {sweetnessLevels.map((level) => (
                            <label key={level.name} className="filter-item">
                                <div className="filter-item__left">
                                    <input
                                        type="radio"
                                        name="sweetness"
                                        className="filter-item__radio"
                                    />
                                    <span className="filter-item__custom-radio"></span>
                                    <span className="filter-item__name">{level.name}</span>
                                </div>
                                <span className="filter-item__quantity">{level.count}</span>
                            </label>
                        ))}
                    </div> 
                </div>
                <div className="alcoFilters__section">
                    <h3 className="filter-title">Price Range</h3>
                    <div className="type__filters">
                        <div className="price-range">
                            <div className="price-range__inputs">
                                <div className="price-range__field">
                                    <input type="text" placeholder="From" className="price-range__input" />
                                    <span className="price-range__currency">$</span>
                                </div>

                                <span className="price-range__divider">-</span>

                                <div className="price-range__field">
                                    <input type="text" placeholder="to" className="price-range__input" />
                                    <span className="price-range__currency">$</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="alcoFilters__section">
                    <h3 className="filter-title">Vibe</h3>
                    <div className="type__filters">
                        {vibeTypes.map((vibe) => (
                            <label key={vibe.name} className="filter-item">
                                <div className="filter-item__left">
                                    <input
                                        type="radio"
                                        name="vibe"
                                        className="filter-item__radio"
                                    />
                                    <span className="filter-item__custom-radio"></span>
                                    <span className="filter-item__name">{vibe.name}</span>
                                </div>
                                <span className="filter-item__quantity">{vibe.count}</span>
                            </label>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}