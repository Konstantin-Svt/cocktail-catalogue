import { useEffect, useState } from "react";
import AgeVerification from "./components/AgeVerification/AgeVerification";
import { Header } from "./components/Header/Header";
import { MainPage } from "./components/MainPage/MainPage";
import { ProductCard } from "./components/ProductCard/ProductCard";
import './styles/grid.scss';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { AlcoFilters, FilterState } from "./components/AlcoFilters/AlcoFilters";
import { fetchCocktails } from "./api/cocktailApi";
import { LogIn } from "./components/LogIn/LogIn";
import { SignUp } from "./components/SignUp/SignUp";
import { Restore } from "./components/Restore/Restore";
import { Profile } from "./components/Profile/Profile";
import { WelcomeStep } from "./components/Steps/WelcomeStep/WelcomeStep";
import { EmailVerification } from "./components/EmailVerification/EmailVerification";
import { RegisterEmailVerification } from "./components/RegisterEmailVerification/RegisterEmailVerification";
import { ChangePassword } from "./components/ChangePassword/ChangePassword";
import { Favorites } from "./components/FavoritesPage/FavoritesPage";

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
        setActiveFilters(prev => ({
            ...prev,
            search: searchQuery
        }));
    }, [searchQuery]);
    
    useEffect(() => {
        const loadInitialData = async () => {
            setIsLoading(true);
            try {
               
                const data = await fetchCocktails(activeFilters, 1);

                setServerData(data);
                setTotalFound(data?.general_count || 0);
            } catch (err) {
                console.error("Помилка завантаження:", err);
            } finally {
                setIsLoading(false);
            }
        };
        loadInitialData();
    }, [activeFilters]);
    
    const location = useLocation();
    const isProductPage = location.pathname.startsWith('/product/');

    const isAuthPage = location.pathname === '/SignUp' || location.pathname === '/LogIn' || location.pathname === '/restore' || location.pathname === '/Profile';
    return (
        <div className="app">
            <AgeVerification onVerified={() => setIsVerified(true)} />
            {!isAuthPage && (
                <Header
                    searchValue={searchQuery}
                    onSearchChange={setSearchQuery}
                    isDisabled={isProductPage}
                />
            )}

            {isVerified && (

                <div className="background">
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
                        <Route path="/LogIn" element={<LogIn />} />
                        <Route path="/SignUp" element={<SignUp />} />
                        <Route path="/restore" element={<Restore />} />
                        <Route path="/Profile" element={<Profile />} />
                        <Route path="/Welcome" element={<WelcomeStep />} />
                        <Route path="/register-verify-email" element={<RegisterEmailVerification />} />
                        <Route path="/verify-email" element={<EmailVerification />} />
                        <Route path="/ChangePassword" element={<ChangePassword />} />
                        <Route path="/Favorites" element={<Favorites searchQuery={searchQuery} onSearchClear={setSearchQuery} />} />
                    </Routes>
                </div>
            )}
        </div>
    );
};