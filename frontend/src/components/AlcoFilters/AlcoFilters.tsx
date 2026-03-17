import './AlcoFilters.scss';
import React, { useEffect, useMemo } from 'react';

const ALCOHOL_TYPE_MAPPING: Record<string, string[]> = {
    'whiskey': ['whiskey'],
    'rum': ['rum', 'dark rum', 'white rum', 'spiced rum'],
    'gin': ['gin', 'dry gin'],
    'vodka': ['vodka'],
    'tequila': ['tequila'],
    'liqueur': ['liqueur'],
    'non-alcoholic': ['non-alcoholic', 'none']
};

const ALCOHOL_LEVELS = ['Non-Alcoholic', 'Low', 'Medium', 'Strong'];
const SWEETNESS_LEVELS = ['Dry', 'Medium', 'Sweet'];
const VIBE_NAMES = ['Party', 'Relax', 'Romantic', 'Energizing'];

interface FilterState {
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
    cocktails: any[];
    allCocktails?: any[]; 
    ingredients: any[];
    setCocktails: (data: any[]) => void;
}

export const AlcoFilters: React.FC<Props> = ({ onFilterChange, filters, cocktails, allCocktails, setCocktails }) => {
    const [tempPrice, setTempPrice] = React.useState<[number, number]>(filters.price);

    const priceTimeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
    const sourceForCounts = allCocktails || cocktails;
    useEffect(() => {
        setTempPrice(filters.price);
    }, [filters.price]);

    useEffect(() => {
        const controller = new AbortController();

        const fetchFilteredCocktails = async () => {
            const params = new URLSearchParams();


            if (filters.search) {
                params.append('search', filters.search);
            }

            if (filters.alcoholType.length > 0) {
                const allTypesToSearch = filters.alcoholType.flatMap(type => {
                    const lowerType = type.toLowerCase();
                    return ALCOHOL_TYPE_MAPPING[lowerType] || [lowerType];
                });
                params.append('types', allTypesToSearch.join(','));
            }

            if (filters.alcoholLevel) params.append('level', filters.alcoholLevel);
            if (filters.sweetnessLevel) params.append('sweetness', filters.sweetnessLevel);
            if (filters.vibe) params.append('vibe', filters.vibe);
            params.append('minPrice', filters.price[0].toString());
            params.append('maxPrice', filters.price[1].toString());

            try {
                const response = await fetch(`http://localhost:5000/api/cocktails?${params.toString()}`, {
                    signal: controller.signal
                });
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                setCocktails(data);
            } catch (error: any) {
                if (error.name !== 'AbortError') console.error(error);
            }
        };

        const timeoutId = setTimeout(fetchFilteredCocktails, 300);
        return () => {
            clearTimeout(timeoutId);
            controller.abort();
        };
    }, [filters, setCocktails]);

    


    const alcoholTypes = useMemo(() => {
        const types = ['Vodka', 'Rum', 'Gin', 'Tequila', 'Whiskey', 'Liqueur', 'Non-alcoholic'];

        return types.map(name => {
 
            const synonyms = (ALCOHOL_TYPE_MAPPING[name.toLowerCase()] || [name.toLowerCase()])
                .map(s => s.toLowerCase());

            const count = sourceForCounts.filter((c: any) => {
                
                const cocktailIngredients = Array.isArray(c.ingredients) ? c.ingredients : [];

               
                return cocktailIngredients.some((ing: string) =>
                    synonyms.includes(ing.toString().toLowerCase().trim())
                );
            }).length;

            return { name, count };
        });
    }, [sourceForCounts]); 

    const alcoholLevels = useMemo(() =>
        ALCOHOL_LEVELS.map(level => ({
            name: level,
            count: sourceForCounts.filter((c: any) => (c.alcohol_level || "").toLowerCase() === level.toLowerCase()).length
        })), [sourceForCounts]);

    const sweetnessLevels = useMemo(() =>
        SWEETNESS_LEVELS.map(level => ({
            name: level,
            count: sourceForCounts.filter((c: any) => (c.sweetness_level || "").toLowerCase() === level.toLowerCase()).length
        })), [sourceForCounts]);

    const vibeTypes = useMemo(() =>
        VIBE_NAMES.map(name => ({
            name,
            count: sourceForCounts.filter((c: any) => {
                const vibes = Array.isArray(c.vibes) ? c.vibes : [];
                return vibes.some((v: any) => (typeof v === 'string' ? v : v.name).toLowerCase() === name.toLowerCase());
            }).length
        })), [sourceForCounts]);


    const handleReset = (e: React.MouseEvent) => {
        e.preventDefault();
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
        const newTypes = filters.alcoholType.includes(name)
            ? filters.alcoholType.filter(t => t !== name)
            : [...filters.alcoholType, name];
        onFilterChange({ ...filters, alcoholType: newTypes });
    };

    const handleRadio = (key: keyof FilterState, value: string) => {
        const newValue = filters[key] === value ? '' : value;
        onFilterChange({ ...filters, [key]: newValue });
    };

    const handlePrice = (val: number, isMin: boolean) => {

        const newPrice = (isMin
            ? [Math.min(val, tempPrice[1]), tempPrice[1]]
            : [tempPrice[0], Math.max(val, tempPrice[0])]) as [number, number];

        setTempPrice(newPrice);


        if (priceTimeoutRef.current) {
            clearTimeout(priceTimeoutRef.current);
        }

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
                            {alcoholTypes.map((type) => (
                                <label key={type.name} className="filter-item">
                                    <div className="filter-item__left">
                                        <input type="checkbox"
                                            className="filter-item__checkbox"
                                            checked={filters.alcoholType.includes(type.name)}
                                            onChange={() => handleCheckbox(type.name)}
                                        />
                                        <span className="filter-item__custom"></span>
                                        <span className="filter-item__name">{type.name}</span>
                                    </div>
                                    <span className="filter-item__quantity">{type.count}</span>
                                </label>
                            ))}
                        </div>
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
                                        checked={filters.alcoholLevel === level.name}
                                        onChange={() => handleRadio('alcoholLevel', level.name)}
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
                                        checked={filters.vibe === vibe.name}
                                        onChange={() => handleRadio('vibe', vibe.name)} />
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