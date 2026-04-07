import axios from "axios";

interface LoginCredentials {
    email: string;
    password: string;
}

const api = axios.create({
    baseURL: "https://cocktail-catalogue-dev.onrender.com",
});

const BASE_URL = "https://cocktail-catalogue-dev.onrender.com";
const API_URL = `${BASE_URL}/api/user`;

export const authApi = {
    login: async (credentials: LoginCredentials) => {
        const response = await api.post('/api/user/token/', credentials);

        if (response.data.access) {
            localStorage.setItem('access_token', response.data.access);
        }
        if (response.data.refresh) {
            localStorage.setItem('refresh_token', response.data.refresh);
        }

        return response.data;
    },

    resendVerification: async (email: string) => {
        const response = await api.post('/api/user/verify-email-resend/', { email });
        return response.data;
    }
};

export const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');

    if (!refresh) {
        throw new Error("No refresh token available");
    }

    const response = await fetch('https://cocktail-catalogue-dev.onrender.com/api/user/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh })
    });

    if (!response.ok) {
        throw new Error("Refresh token expired");
    }

    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data.access;
};

export const passwordApi = {
    requestReset: async (email: string) => {
        const response = await axios.post(`${API_URL}/reset-password/`, { email });
        return response.data;
    },

   
    resendResetEmail: async (email: string) => {
        const response = await axios.post(`${API_URL}/reset-password/`, { email });
        return response.data;
    },


    confirmReset: async (data: { uid: string; token: string; new_password: string }) => {
        const response = await axios.post(`${API_URL}/reset-password-confirm/`, data);
        return response.data;
    }
};