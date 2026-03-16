import AgeVerification from "./components/AgeVerification/AgeVerification";
import { Header } from "./components/Header/Header";
import { MainPage } from "./components/MainPage/MainPage";
import { ProductCard } from "./components/ProductCard/ProductCard";
import './styles/grid.scss';
import { Routes, Route } from 'react-router-dom';

export const App = () => (
        <div className="app">
            <AgeVerification />
            <Header />
            <Routes>
                <Route path="/" element={<MainPage />} />
                <Route path="/product/:id" element={<ProductCard />} />
                <Route path="/catalog" element={<MainPage />} />
            </Routes>
        </div>
)