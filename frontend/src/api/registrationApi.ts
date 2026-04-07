import axios from 'axios';
import { BASE_URL } from './cocktailApi';

export const api = axios.create({
    baseURL: BASE_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
    credentials: 'include',
});

export const registrationApi = {
    register: (userData: any) => api.post('/user/register/', userData),
    resendVerification: (email: string) => api.post('/user/verify-resend/', { email }),
    verifyEmail: (uid: string, token: string) => api.get(`/user/verify-email/?uid=${uid}&token=${token}`),
    updateProfile: (profileData: any) => api.patch('/user/me/', profileData),
    login: (credentials: any) => api.post('/user/token/', credentials),
    refresh: () => api.post('/user/token/refresh/'),
    getMe: () => api.get('/user/me/'),
};