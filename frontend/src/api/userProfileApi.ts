import { refreshToken } from "./authApi";

const BASE_URL = 'https://cocktail-catalogue-dev.onrender.com/api';

const apiFetch = async (endpoint: string, options: RequestInit = {}) => {
    let token = localStorage.getItem('access_token');

    const makeRequest = async (tokenToUse: string | null) => {
        return await fetch(`${BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${tokenToUse}`,
                ...options.headers,
            },
        });
    };

    let response = await makeRequest(token);

    if (response.status === 401) {
        try {
            console.log(`Token expired for ${endpoint}, refreshing...`);
            const newToken = await refreshToken();
            response = await makeRequest(newToken);
        } catch (err) {
            throw new Error("401");
        }
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error ${response.status}`);
    }

    return response;
};

export const fetchUserProfile = async () => {
    const response = await apiFetch('/user/me/');
    return await response.json();
};

export const changePassword = async (passwordData: any) => {
    const response = await apiFetch('/user/me/change-password/', {
        method: 'POST',
        body: JSON.stringify(passwordData),
    });
    return await response.json();
};

export const requestEmailChange = async (newEmail: string, currentPassword: string) => {
    await apiFetch('/user/me/change-email/', {
        method: 'POST',
        body: JSON.stringify({
            new_email: newEmail,
            password: currentPassword
        }),
    });
    return true;
};

export const verifyEmailChange = async (tokenParam: string) => {

    const response = await fetch(`${BASE_URL}/user/me/change-email-verify/?token=${tokenParam}`);
    if (!response.ok) throw new Error('Email verification failed');
    return await response.json();
};