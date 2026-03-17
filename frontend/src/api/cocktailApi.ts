const BASE_URL = 'https://cocktail-catalogue.onrender.com/api';

const ALCOHOL_SYNONYMS: Record<string, string[]> = {
    'whiskey': ['whiskey', 'bourbon', 'scotch', 'rye', 'whisky'],
    'rum': ['rum', 'dark rum', 'white rum', 'spiced rum'],
    'gin': ['gin', 'dry gin'],
    'vodka': ['vodka']
};

export const fetchCocktails = () => fetch(`${BASE_URL}/cocktails/`).then(res => res.json());
export const fetchIngredients = () => fetch(`${BASE_URL}/ingredients/`).then(res => res.json());
export const fetchVibes = () => fetch(`${BASE_URL}/vibes/`).then(res => res.json());

export const fetchFilteredCocktails = (filters: any = {}) => {
    const params = new URLSearchParams();


    if (filters.search) {
        params.append('search', filters.search);
    }

    if (filters.alcoholType?.length) {
        const typesToSend = new Set<string>();

        filters.alcoholType.forEach((type: string) => {
            const lowerType = type.toLowerCase();
            if (ALCOHOL_SYNONYMS[lowerType]) {
                ALCOHOL_SYNONYMS[lowerType].forEach(syn => typesToSend.add(syn));
            } else {
                typesToSend.add(lowerType);
            }
        });

        params.append('alcohol_type', Array.from(typesToSend).join(','));
    }

    if (filters.alcoholLevel) params.append('alcohol_level', filters.alcoholLevel.toLowerCase());
    if (filters.sweetnessLevel) params.append('sweetness_level', filters.sweetnessLevel.toLowerCase());


    if (filters.vibe) params.append('vibe', filters.vibe.toLowerCase());

    if (filters.price && Array.isArray(filters.price)) {
        params.append('min_price', filters.price[0].toString());
        params.append('max_price', filters.price[1].toString());
    }

    return fetch(`${BASE_URL}/cocktails/?${params.toString()}`)
        .then(res => res.json())
        .then(data => Array.isArray(data) ? data : data.results || []);
};