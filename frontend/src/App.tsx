import { useState } from "react";
import AgeVerification from "./components/AgeVerification/AgeVerification";
import { Header } from "./components/Header/Header";
import { MainPage } from "./components/MainPage/MainPage";
import { ProductCard } from "./components/ProductCard/ProductCard";
import './styles/grid.scss';
import { Routes, Route } from 'react-router-dom';

export const App = () => {
    const [searchQuery, setSearchQuery] = useState("");
    const [isVerified, setIsVerified] = useState(false);

    return (
        <div className="app">
            <AgeVerification onVerified={() => setIsVerified(true)} />
            <Header searchValue={searchQuery} onSearchChange={setSearchQuery} />

            {isVerified && (
                <Routes>
                    <Route path="/" element={<MainPage searchQuery={searchQuery}/>} />
                    <Route path="/product/:id" element={<ProductCard />} />
                    <Route path="/catalog" element={<MainPage searchQuery={searchQuery}/>} />
                </Routes>
            )}
        </div>
)
}