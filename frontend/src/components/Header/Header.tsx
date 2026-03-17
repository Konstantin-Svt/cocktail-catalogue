import './Header.scss';

interface HeaderProps {
    searchValue: string;
    onSearchChange: (val: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ searchValue, onSearchChange }) => {
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
                value={searchValue}
                onChange={(e) => onSearchChange(e.target.value)}/>
            </div>
        </header>
    )
}