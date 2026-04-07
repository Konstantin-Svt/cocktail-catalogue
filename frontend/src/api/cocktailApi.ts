import { FilterState } from "../components/AlcoFilters/AlcoFilters";

const DEFAULT_URL = 'https://cocktail-catalogue.onrender.com/api';
export const BASE_URL = (import.meta as any).env?.VITE_API_URL || DEFAULT_URL;


export const fetchCocktails = async (filters: FilterState, page: number = 1) => {
    const params = new URLSearchParams();


    if (filters.alcoholType?.length) {
        params.append('ingredients', filters.alcoholType.join(',').toLowerCase());
    }


    if (filters.alcoholLevel) params.append('alcohol_level', filters.alcoholLevel.toLowerCase());
    if (filters.sweetnessLevel) params.append('sweetness_level', filters.sweetnessLevel.toLowerCase());
    if (filters.vibe) params.append('vibes', filters.vibe.toLowerCase());
    if (filters.search) params.append('search', filters.search);


    params.append('min_price', filters.price[0].toString());
    params.append('max_price', filters.price[1].toString());


    params.append('page', page.toString());
    params.append('page_size', '12');


    const response = await fetch(`${BASE_URL}/cocktails/?${params.toString()}`, {
        method: 'GET',
        credentials: 'include',
    });

    if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
};

export const fetchCocktailById = async (id: string) => {
    const response = await fetch(`${BASE_URL}/cocktails/${id}/`, {
        method: 'GET',
        credentials: 'include',
    });

    if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
    }

    return response.json();
};

export const sendAnalyticsEvent = (payload: Record<string, unknown>) => {
    try {
        fetch(`${BASE_URL}/analytics/events/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
    } catch (error) {
        console.error('Analytics error:', error);
    }
};