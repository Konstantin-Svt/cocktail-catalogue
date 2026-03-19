import { FilterState } from "../components/AlcoFilters/AlcoFilters";


export const fetchCocktails = async (filters: FilterState, page: number = 1) => {
    const params = new URLSearchParams();


    if (filters.alcoholType?.length) {
        filters.alcoholType.forEach((t: string) =>
            params.append('ingredients', t.toLowerCase())
        );
    }


    if (filters.alcoholLevel) params.append('alcohol_level', filters.alcoholLevel.toLowerCase());
    if (filters.sweetnessLevel) params.append('sweetness_level', filters.sweetnessLevel.toLowerCase());
    if (filters.vibe) params.append('vibes', filters.vibe.toLowerCase());
    if (filters.search) params.append('search', filters.search);


    params.append('min_price', filters.price[0].toString());
    params.append('max_price', filters.price[1].toString());


    params.append('page', page.toString());
    params.append('page_size', '12');

    const BASE_URL = 'https://cocktail-catalogue-dev.onrender.com/api';


    const response = await fetch(`${BASE_URL}/cocktails/?${params.toString()}`);

    if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
};