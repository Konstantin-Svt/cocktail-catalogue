import { Link } from 'react-router-dom';
import './Header.scss';
import { useEffect, useRef, useState } from 'react';

interface HeaderProps {
    searchValue: string;
    onSearchChange: (val: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ searchValue, onSearchChange }) => {
    const [localValue, setLocalValue] = useState(searchValue);
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);
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
                    onBlur={() => !localValue && setIsSearchOpen(false)}/>
                <button className="header__search-btn" onClick={toggleSearch} type="button" /> 
            </div>

            </div>
        </header>
    )
}