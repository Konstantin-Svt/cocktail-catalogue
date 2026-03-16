import './Header.scss';

export const Header = () => {
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
                maxLength={26}/>
            </div>
        </header>
    )
}