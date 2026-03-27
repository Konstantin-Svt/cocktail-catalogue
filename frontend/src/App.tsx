import { useEffect, useState } from "react";
import AgeVerification from "./components/AgeVerification/AgeVerification";
import { Header } from "./components/Header/Header";
import { MainPage } from "./components/MainPage/MainPage";
import { ProductCard } from "./components/ProductCard/ProductCard";
import './styles/grid.scss';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { AlcoFilters, FilterState } from "./components/AlcoFilters/AlcoFilters";
import { fetchCocktails } from "./api/cocktailApi";

export const App = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [isVerified, setIsVerified] = useState(() => {
        return localStorage.getItem('ageVerified') === 'true';
    });
    const [totalFound, setTotalFound] = useState(0);
    const [activeFilters, setActiveFilters] = useState<FilterState>({
        alcoholType: [],
        alcoholLevel: '',
        price: [0, 180],
        sweetnessLevel: '',
        vibe: '',
        search: '',
    });
    const [serverData, setServerData] = useState<any>(null);

    const mainPageElement = (
        <MainPage
            searchQuery={searchQuery}
            activeFilters={activeFilters}
            setActiveFilters={setActiveFilters}
            serverData={serverData}
            isLoading={isLoading}
        />
    );


    useEffect(() => {
        const loadInitialData = async () => {
            setIsLoading(true);
            try {
                const data = await fetchCocktails(activeFilters, 1);
                setServerData(data);
                setTotalFound(data?.general_count || 0);
            } catch (err) {
                console.error("Data fetch failed:", err);
            } finally {
                setIsLoading(false);
            }
        };

        loadInitialData();
    }, [activeFilters]);
    
    const location = useLocation();
    const isProductPage = location.pathname.startsWith('/product/');
    return (
        <div className="app">
            <AgeVerification onVerified={() => setIsVerified(true)} />
            <Header searchValue={searchQuery} onSearchChange={setSearchQuery} isDisabled={isProductPage} />

            {isVerified && (
                <Routes>
                    <Route path="/" element={mainPageElement} />
                    <Route path="/catalog" element={mainPageElement} />

                    <Route path="/filters" element={
                        <div className="mobile-filters-layout">
                            <div className="mobile-filters-header">
                                <Link to="/" className="back-link">← Back</Link>
                                <h2>Filters</h2>
                            </div>
                            <AlcoFilters
                                filters={activeFilters}
                                onFilterChange={setActiveFilters}
                                summary={serverData}
                            />
                            <div className="show-results-btn__container">
                                <Link to="/" className="show-results-btn">Show {totalFound} cocktails</Link>
                            </div>
                        </div>
                    } />

                    <Route path="/product/:id" element={<ProductCard />} />
                </Routes>
            )}
        </div>
    );
};