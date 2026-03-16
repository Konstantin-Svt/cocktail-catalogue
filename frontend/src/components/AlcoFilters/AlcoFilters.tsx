import './AlcoFilters.scss';
import React, { useState } from 'react';

interface FilterState {
    alcoholType: string[];
    alcoholLevel: string;
    price: [number, number];
    sweetnessLevel: string;
    vibe: string;
}

interface Props {
    onFilterChange: React.Dispatch<React.SetStateAction<FilterState>>;
    filters: FilterState;
}

export const AlcoFilters: React.FC<Props> = ({ onFilterChange, filters }) => {
    
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
        { name: 'Non-Alcoholic', count: 67 },
        { name: 'Low', count: 23 },
        { name: 'Medium', count: 58 },
        { name: 'Strong', count: 32 },
    ];
    const sweetnessLevels = [
        { name: 'Dry', count: 16 },
        { name: 'Medium', count: 21 },
        { name: 'Sweet', count: 46 },
    ];
    const vibeTypes = [
        { name: 'Party', count: 12 },
        { name: 'Romantic', count: 21 },
        { name: 'Summer', count: 43 },
        { name: 'Tropical', count: 23 },
        { name: 'Classic', count: 12 },
    ];

    const totalMax = 180;

    const trackStyle = {
        left: `${(filters.price[0] / totalMax) * 100}%`,
        right: `${100 - (filters.price[1] / totalMax) * 100}%`
    };
    const handleReset = (e: React.MouseEvent) => {
        e.preventDefault();
        onFilterChange({
            alcoholType: [],
            alcoholLevel: '',
            price: [0, 180],
            sweetnessLevel: '',
            vibe: '',
        });
    };
    const handleCheckbox = (name: string) => {
        const newTypes = filters.alcoholType.includes(name)
            ? filters.alcoholType.filter(t => t !== name)
            : [...filters.alcoholType, name];
        onFilterChange({ ...filters, alcoholType: newTypes });
    };

    const handleRadio = (key: keyof FilterState, value: string) => {
        onFilterChange({ ...filters, [key]: value });
    };

    const handlePrice = (val: number, isMin: boolean) => {
        const newPrice = (isMin
            ? [val, filters.price[1]]
            : [filters.price[0], val]) as [number, number];

        onFilterChange(prev => ({
            ...prev,
            price: newPrice
        }));
    };

    return (
        <div className="alcoFilters">
            <div className="alcoFilters__sections">
                <div className="alcoFilters__section">
                    <div className="section__right">Your Filters</div>
                    <div className="section__left">
                        <a href="" className='reset__text' onClick={handleReset}><span className="reset__icon"></span> Reset Filters</a>
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
                                        <input type="checkbox" 
                                        className="filter-item__checkbox" 
                                        checked={filters.alcoholType.includes(type.name)}
                                        onChange={() => handleCheckbox(type.name)} />
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
                                    <input 
                                    type="radio" 
                                    name="alcohol-level" 
                                    className="filter-item__radio"
                                    checked={filters.alcoholLevel === level.name}
                                    onChange={() => handleRadio('alcoholLevel', level.name)} />
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
                                        checked={filters.sweetnessLevel === level.name}
                                        onChange={() => handleRadio('sweetnessLevel', level.name)}
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
                    <div className="type__filters">
                        <div className="price-range">
                            <h3 className="price-range__title">Price Range</h3>
                            <div className="price-range__display">
                                {filters.price[0]} $ - {filters.price[1]} $ +
                            </div>

                            <div className="range-slider-root">
                                <div className="range-slider-track" style={trackStyle}></div>

                                <input
                                    type="range"
                                    min="0"
                                    max={totalMax}
                                    value={filters.price[0]}
                                    onChange={(e) => handlePrice(Number(e.target.value), true)}
                                    className="range-input"
                                />
                                <input
                                    type="range"
                                    min="0"
                                    max={totalMax}
                                    value={filters.price[1]}
                                    onChange={(e) => handlePrice(Number(e.target.value), false)}
                                    className="range-input"
                                />
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
                                        checked={filters.vibe === vibe.name}
                                        onChange={() => handleRadio('vibe', vibe.name)}
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