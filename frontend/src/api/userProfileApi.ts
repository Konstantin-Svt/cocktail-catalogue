import { refreshToken } from "./authApi";

const BASE_URL = 'https://cocktail-catalogue-dev.onrender.com/api';

const apiFetch = async (endpoint: string, options: RequestInit = {}) => {

    let token = localStorage.getItem('access_token');

    const makeRequest = async (tokenToUse: string | null) => {

        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string>), 
        };


        if (tokenToUse) {
            headers['Authorization'] = `Bearer ${tokenToUse}`;
        }

        return await fetch(`${BASE_URL}${endpoint}`, {
            ...options,
            headers: headers, 
        });
    };

    let response = await makeRequest(token);

    if (response.status === 401) {
        try {
            console.log(`Token expired for ${endpoint}, refreshing...`);
            const newToken = await refreshToken();

            if (newToken) {
                localStorage.setItem('access_token', newToken);
                response = await makeRequest(newToken);
            }
        } catch (err) {
            console.error("Critical Auth Error: Refresh failed");
            localStorage.removeItem('access_token');
            throw new Error("401");
        }
    }

    if (!response.ok) {
        // Читаємо деталі помилки від сервера
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

export const verifyEmailChange = async (uid: string, token: string) => {
    const response = await apiFetch(`/user/me/change-email-verify/?uid=${uid}&token=${token}`, {
        method: 'GET'
    });

    if (response.status === 204) return { detail: "Success" };
    return await response.json();
};

export const verifyEmail = async (uid: string, token: string) => {
    const response = await fetch(`${BASE_URL}/verify-email/?uid=${uid}&token=${token}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Verification failed');
    }
    return data; 
};

export const updatePassword = async (oldPassword: string, newPassword: string) => {
    const response = await apiFetch('/user/me/change-password/', {
        method: 'POST',
        body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword
        }),
    });
    return await response.json();
};