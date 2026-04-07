import { Link } from 'react-router-dom';
import './WelcomeStep.scss';

export const WelcomeStep = () => (
    <div className="welcome-step">
        <div className="welcome-step__content">
            <div className="welcome-step__image-wrapper">
                {/* Використовуй іконку коктейлю з макета */}
                <div className="welcome-step__icon"></div>
            </div>

            <h2 className="welcome-step__title">Welcome to “Drinkly”</h2>

            <p className="welcome-step__subtitle">
                We’re happy to see you in our app
            </p>

            <Link
                to="/"
                className="welcome-step__btn-go"
            >
                Go to Bar
            </Link>
        </div>
    </div>
);