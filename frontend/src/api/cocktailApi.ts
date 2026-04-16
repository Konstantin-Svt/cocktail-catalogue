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

// cocktailApi.ts

export const fetchComments = async (cocktailId: string) => {
    // 1. Прибираємо фільтрацію (?cocktail_id=...), беремо все підряд
    const response = await fetch(`${BASE_URL}/review/`);

    if (!response.ok) throw new Error('Failed to fetch comments');

    const data = await response.json();
    const allReviews = data.results || [];

    // 2. ДЛЯ ТЕСТУ: повертаємо ВСІ коментарі без фільтрації
    // Якщо після цього коментар з'явиться — значить бекенд не вміє фільтрувати.
    return allReviews;
};
// Відправка коментаря
export const postComment = async (cocktailId: string, text: string, mark: number) => {
    // 1. Використовуємо правильний ключ токена, який ми бачили в Local Storage
    const token = localStorage.getItem('access_token');

    if (!token) {
        throw new Error('You must be logged in to post a review');
    }

    // 2. Валідація тексту (мінімум 5 символів згідно зі схемою)
    const trimmedText = text.trim();
    if (trimmedText.length < 5) {
        throw new Error('Review text must be at least 5 characters long');
    }

    // 3. Формуємо тіло запиту відповідно до схеми CreateReview
    const body = {
        text: trimmedText,
        mark: Math.floor(mark) || 5, // Рейтинг як integer
        cocktail_id: parseInt(cocktailId, 10), // ID як integer
        parent_id: null // Обов'язкове поле для відповіді, згідно зі схемою
    };

    const response = await fetch(`${BASE_URL}/review/add-review/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json', // Додай це
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(body)
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // Обробка помилки 400 Bad Request
        if (response.status === 400) {
            console.error('Validation error details:', errorData);
            throw new Error(errorData.detail || 'Validation error: check your input');
        }

        // Обробка помилки 500
        throw new Error(errorData.detail || `Server error: ${response.status}`);
    }

    return response.json();
};