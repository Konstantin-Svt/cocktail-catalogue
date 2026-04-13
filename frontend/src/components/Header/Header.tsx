import { Link } from 'react-router-dom';
import './Header.scss';
import { useEffect, useRef, useState } from 'react';

interface HeaderProps {
    searchValue: string;
    onSearchChange: (val: string) => void;
    isDisabled?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ searchValue, onSearchChange, isDisabled }) => {
    const [localValue, setLocalValue] = useState(searchValue);
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);

    const isAuthenticated = !!localStorage.getItem('access_token');
    
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            
            if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
                setIsSearchOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);
    useEffect(() => {
        const handler = setTimeout(() => {
            onSearchChange(localValue);
        }, 800);

        return () => clearTimeout(handler);
    }, [localValue]);
    useEffect(() => {
        setLocalValue(searchValue);
    }, [searchValue]);

    const toggleSearch = () => {
        setIsSearchOpen(!isSearchOpen);
    };
    return (
        <header className="header">
            <div 
            className="header__left">
                <Link to='/'>
                    <button className='header__button'></button>
                </Link>
                </div>
            <div 
            className="header__right"> 
                <div 
                ref={searchRef}
                className={`header__search-container ${isSearchOpen ? 'header__search-container--open' : ''}`}>
                    <input 
                        type="text" 
                        className="header__input" 
                        placeholder='Search cocktails or ingredients'
                        maxLength={50}
                        value={localValue}
                        onChange={(e) => setLocalValue(e.target.value)}
                        autoFocus={isSearchOpen}
                        onBlur={() => !localValue && setIsSearchOpen(false)}
                        disabled={isDisabled}/>
                    <button className="header__search-btn" onClick={toggleSearch} type="button" /> 
                </div>
                <div className="header__auths">
                    {isAuthenticated ? (
                        <div className="header__user-menu" style={{ display: 'flex', gap: '15px' }}>
                            <Link to='/Favorites' className="header__icon-btn header__icon-btn--heart"></Link>
                            <Link to='/Profile'className="header__avatar-wrapper">
                                
                            </Link>
                        </div>
                    ) : (
                        <>
                            <div className="header__auth-desktop">
                                <Link to='/SignUp'>
                                    <button className="header__auth header__signUp">Sign up</button>
                                </Link>
                                <Link to='/LogIn'>
                                    <button className="header__auth header__logIn">Log in</button>
                                </Link>
                            </div>
                            <Link to='/LogIn' className="header__auth-mobile">
                                <button className="header__profile-btn" type="button" />
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </header>
    )
}