import './AlcoFilters.scss';
import React, { useEffect, useMemo } from 'react';
import { sendAnalyticsEvent, } from '../../api/cocktailApi';

export interface FilterState {
    alcoholType: string[];
    alcoholLevel: string;
    price: [number, number];
    sweetnessLevel: string;
    vibe: string;
    search: string;
}

interface Props {
    onFilterChange: React.Dispatch<React.SetStateAction<FilterState>>;
    filters: FilterState;
    summary: any;
}

export const AlcoFilters: React.FC<Props> = ({ onFilterChange, filters, summary }) => {
    const [tempPrice, setTempPrice] = React.useState<[number, number]>(filters.price);
    const [aiQuery, setAiQuery] = React.useState('');
    const [isAiProcessing, setIsAiProcessing] = React.useState(false);
    const [aiResponse, setAiResponse] = React.useState<string | null>(null);
    const socketRef = React.useRef<WebSocket | null>(null);
    const priceTimeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(() => {
        setTempPrice(filters.price);
    }, [filters.price]);
    useEffect(() => {
        socketRef.current = new WebSocket('wss://cocktail-catalogue-dev.onrender.com/ws/aifilters/');

        socketRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('AI Response:', data);

            // Зберігаємо текст повідомлення для відображення
            if (data.message) {
                setAiResponse(data.message);
            }

            // Якщо сервер також надсилає фільтри для автоматичного застосування:
            if (data.filters) {
                onFilterChange(prev => ({ ...prev, ...data.filters }));
            }

            setIsAiProcessing(false);
        };

        return () => {
            socketRef.current?.close();
        };
    }, [onFilterChange]);

    const handleAiSearch = () => {
        if (aiQuery.trim() && socketRef.current?.readyState === WebSocket.OPEN) {
            setIsAiProcessing(true);
            socketRef.current.send(JSON.stringify({ message: aiQuery }));
            setAiQuery(''); 
        }
    };
    const alcoholTypes = useMemo(() => {
        if (!summary?.ingredients_count) return [];
        return Object.entries(summary.ingredients_count).map(([key, count]) => ({
            name: key,
            count: count as number
        }));
    }, [summary]);

    const alcoholLevels = useMemo(() => {
        if (!summary?.alcohol_level_count) return [];
        return Object.entries(summary.alcohol_level_count).map(([key, count]) => ({
            name: key.charAt(0).toUpperCase() + key.slice(1),
            count: count as number
        }));
    }, [summary]);


    const sweetnessLevels = useMemo(() => {
        if (!summary?.sweetness_level_count) return [];
        return Object.entries(summary.sweetness_level_count).map(([key, count]) => ({
            name: key.charAt(0).toUpperCase() + key.slice(1),
            count: count as number
        }));
    }, [summary]);


    const vibeTypes = useMemo(() => {
        if (!summary?.vibes_count) return [];
        return Object.entries(summary.vibes_count).map(([key, count]) => ({
            name: key.charAt(0).toUpperCase() + key.slice(1),
            count: count as number
        }));
    }, [summary]);


    const handleReset = (e: React.MouseEvent) => {
        e.preventDefault();
        sendAnalyticsEvent({
            event_name: `filters_reset`,
            previous_filters: JSON.stringify(filters)
        });
        onFilterChange({
            alcoholType: [],
            alcoholLevel: '',
            price: [0, 180],
            sweetnessLevel: '',
            vibe: '',
            search: '',
        });
    };

    const handleCheckbox = (name: string) => {
        const val = name.toLowerCase();
        const newTypes = filters.alcoholType.includes(val)
            ? filters.alcoholType.filter(t => t !== val)
            : [...filters.alcoholType, val];
        onFilterChange({ ...filters, alcoholType: newTypes });
    };

    const handleRadio = (key: keyof FilterState, value: string) => {
        const val = value.toLowerCase();
        const newValue = filters[key] === val ? '' : val;
        onFilterChange({ ...filters, [key]: newValue });
    };

    const handlePrice = (val: number, isMin: boolean) => {
        const newPrice = (isMin
            ? [Math.min(val, tempPrice[1]), tempPrice[1]]
            : [tempPrice[0], Math.max(val, tempPrice[0])]) as [number, number];

        setTempPrice(newPrice);

        if (priceTimeoutRef.current) clearTimeout(priceTimeoutRef.current);
        priceTimeoutRef.current = setTimeout(() => {
            onFilterChange(prev => ({ ...prev, price: newPrice }));
        }, 800);
    };

    const totalMax = 180;
    const trackStyle = {
        left: `${(tempPrice[0] / totalMax) * 100}%`,
        right: `${100 - (tempPrice[1] / totalMax) * 100}%`
    };

    return (
        <div className="alcoFilters">
            <div className="alcoFilters__sections">
                <div className="alcoFilters__section section-header">
                    <div className="section__right">Your Filters</div>
                    <div className="section__left">
                        <a href="#" className='reset__text' onClick={handleReset}>
                            <span className="reset__icon"></span> Reset Filters
                        </a>
                    </div>
                </div>

                {/* Alcohol Type Section */}
                <div className="alcoFilters__section">
                    <div className="alcoFilters__section-type">
                        <div className="type__title">Alcohol Type</div>
                        <div className="type__filters">
                            {alcoholTypes.map((type) => {
                                const typeNameLower = type.name.toLowerCase();
                                const isChecked = filters.alcoholType.includes(typeNameLower);

                                return (
                                    <label key={type.name} className="filter-item">
                                        <div className="filter-item__left">
                                            <input
                                                type="checkbox"
                                                className="filter-item__checkbox"
                                                checked={isChecked}
                                                onChange={() => handleCheckbox(typeNameLower)}
                                            />
                                            <span className="filter-item__custom"></span>
                                            <span className="filter-item__name">{type.name}</span>
                                        </div>
                                        <span className="filter-item__quantity">{type.count}</span>
                                    </label>
                                );
                            })}
                        </div>
                    </div>
                </div>
                <div className="alcoFilters__section">
                    <div className="intelligent-filters">
                        <div className="intelligent-filters__header">
                            <span className="intelligent-filters__icon"></span>
                            <h3 className="intelligent-filters__title">Intelligent Filters:</h3>
                        </div>

                        <p className="intelligent-filters__question">What are you looking for?</p>

                        <div className="intelligent-filters__input-wrapper">
                            <textarea
                                className="intelligent-filters__input"
                                placeholder="Which ingredients are you interested in? I'll find cocktails based on them"
                                value={aiQuery}
                                onChange={(e) => setAiQuery(e.target.value)}
                            />
                        </div>

                        {/* Блок з відповіддю AI */}
                        {aiResponse && (
                            <div className="intelligent-filters__result">
                                <p className="ai-message-text">{aiResponse}</p>
                                <button className="clear-ai-btn" onClick={() => setAiResponse(null)}>Clear results</button>
                            </div>
                        )}

                        <button
                            className="intelligent-filters__search-btn"
                            onClick={handleAiSearch}
                            disabled={isAiProcessing}
                        >
                            {isAiProcessing ? 'Searching...' : 'Search'}
                        </button>
                    </div>
                </div>
                {/* Alcohol Level */}
                <div className="alcoFilters__section">
                    <h3 className="filter-title">Alcohol Level</h3>
                    <div className="type__filters">
                        {alcoholLevels.map((level) => (
                            <label key={level.name} className="filter-item">
                                <div className="filter-item__left">
                                    <input type="radio"
                                        name="alcohol-level"
                                        className="filter-item__radio"
                                        onChange={() => handleRadio('alcoholLevel', level.name.toLowerCase())}
                                        checked={filters.alcoholLevel.toLowerCase() === level.name.toLowerCase()}
                                    />
                                    <span className="filter-item__custom-radio"></span>
                                    <span className="filter-item__name">{level.name}</span>
                                </div>
                                <span className="filter-item__quantity">{level.count}</span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Sweetness */}
                <div className="alcoFilters__section">
                    <h3 className="filter-title">Sweetness Level</h3>
                    <div className="type__filters">
                        {sweetnessLevels.map((level) => (
                            <label key={level.name} className="filter-item">
                                <div className="filter-item__left">
                                    <input type="radio"
                                        name="sweetness"
                                        className="filter-item__radio"
                                        checked={filters.sweetnessLevel.toLowerCase() === level.name.toLowerCase()}
                                        onChange={() => handleRadio('sweetnessLevel', level.name.toLowerCase())}
                                    />
                                    <span className="filter-item__custom-radio"></span>
                                    <span className="filter-item__name">{level.name}</span>
                                </div>
                                <span className="filter-item__quantity">{level.count}</span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Price Range */}
                <div className="alcoFilters__section">
                    <div className="price-range">
                        <h3 className="price-range__title">Price Range</h3>
                        <div className="price-range__display">
                            {tempPrice[0]} $ - {tempPrice[1]} $ +
                        </div>
                        <div className="range-slider-root">
                            <div className="range-slider-track" style={trackStyle}></div>
                            <input type="range" min="0" max={totalMax} value={tempPrice[0]}
                                onChange={(e) => handlePrice(Number(e.target.value), true)}
                                className="range-input" />
                            <input type="range" min="0" max={totalMax} value={tempPrice[1]}
                                onChange={(e) => handlePrice(Number(e.target.value), false)}
                                className="range-input" />
                        </div>
                    </div>
                </div>

                {/* Vibe */}
                <div className="alcoFilters__section">
                    <h3 className="filter-title">Vibe</h3>
                    <div className="type__filters">
                        {vibeTypes.map((vibe) => (
                            <label key={vibe.name} className="filter-item">
                                <div className="filter-item__left">
                                    <input type="radio" name="vibe" className="filter-item__radio"
                                        checked={filters.vibe.toLowerCase() === vibe.name.toLowerCase()}
                                        onChange={() => handleRadio('vibe', vibe.name.toLowerCase())} />
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
    );
};