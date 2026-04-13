import { configureStore } from '@reduxjs/toolkit';
import { favoritesApi } from '../api/favoritesApi';

export const store = configureStore({
    reducer: {
        [favoritesApi.reducerPath]: favoritesApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware().concat(favoritesApi.middleware),
});


export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;