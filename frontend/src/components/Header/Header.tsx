import './Header.scss';
import { useEffect, useState } from 'react';

interface HeaderProps {
    searchValue: string;
    onSearchChange: (val: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ searchValue, onSearchChange }) => {
    const [localValue, setLocalValue] = useState(searchValue);

    useEffect(() => {
        const handler = setTimeout(() => {
            onSearchChange(localValue);
        }, 800);

        return () => clearTimeout(handler);
    }, [localValue]);
    useEffect(() => {
        setLocalValue(searchValue);
    }, [searchValue]);

    return (
        <header className="header">
            <div 
            className="header__left">
                <button className='header__button'>

                </button>
                <div 
            className="header__logo">
                </div>
                </div>
            <div 
            className="header__right"> 
            <input 
                type="text" 
                className="header__input" 
                placeholder='Search cocktails or ingredients'
                maxLength={50}
                value={localValue}
                onChange={(e) => setLocalValue(e.target.value)}/>
            </div>
        </header>
    )
}