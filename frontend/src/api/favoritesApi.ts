import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const favoritesApi = createApi({
    reducerPath: 'favoritesApi',
    baseQuery: fetchBaseQuery({
        // Використовуємо пряму адресу сервера замість /api
        baseUrl: 'https://cocktail-catalogue-dev.onrender.com/api',
        prepareHeaders: (headers) => {
            const token = localStorage.getItem('access_token');
            if (token) {
                // Обов'язково очищаємо токен від можливих лапок
                headers.set('authorization', `Bearer ${token.replace(/"/g, '')}`);
            }
            return headers;
        },
    }),
    tagTypes: ['Favorite'],
    endpoints: (builder) => ({
        getFavorites: builder.query<any[], void>({
            // Точно як у Swagger: /api/ вже в baseUrl, додаємо решту зі слейшем
            query: () => 'user/me/favourites/',
            providesTags: ['Favorite'],
        }),
        addToFavorites: builder.mutation<void, { cocktail_id: number }>({
            query: (body) => ({
                url: 'user/me/add-favourites/',
                method: 'POST',
                body,
            }),
            invalidatesTags: ['Favorite'],
        }),
        removeFromFavorites: builder.mutation<void, { cocktail_id: number }>({
            query: (body) => ({
                url: 'user/me/remove-favourites/',
                method: 'POST',
                body,
            }),
            invalidatesTags: ['Favorite'],
        }),
    }),
});

export const {
    useGetFavoritesQuery,
    useAddToFavoritesMutation,
    useRemoveFromFavoritesMutation
} = favoritesApi;