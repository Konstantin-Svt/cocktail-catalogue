import React, { useState, useEffect } from 'react';
import './AgeVerification.scss';
import { sendAnalyticsEvent } from '../../api/cocktailApi';

interface AgeVerificationProps {
    onVerified: () => void;
}

const AgeVerification: React.FC<AgeVerificationProps> = ({ onVerified }) => {
    const [isVisible, setIsVisible] = useState(false);
    const [isUnderage, setIsUnderage] = useState(() => {
        return localStorage.getItem('ageDenied') === 'true';
    });

    useEffect(() => {
        const isVerified = localStorage.getItem('ageVerified');
        const isDenied = localStorage.getItem('ageDenied');

       
        if (!isVerified || isDenied === 'true') {
            setIsVisible(true);
        }
    }, []);
  
    const handleConfirm = () => {
        sendAnalyticsEvent({ event_name: 'age_confirmation', age_confirmed: true });
        onVerified();
        localStorage.setItem('ageVerified', 'true');
        setIsVisible(false);
    };

    const handleReject = () => {
        sendAnalyticsEvent({ event_name: 'age_confirmation', age_confirmed: false });
        setIsUnderage(true); // Замість редиректу показуємо повідомлення
    };

    if (!isVisible) return null;

    return (
        <div className="age-modal">
            <div className="age-modal__content">
                <div className='age-modal__badge'>18+</div>

                {!isUnderage ? (
                    // ОСНОВНИЙ ЕКРАН ПЕРЕВІРКИ
                    <>
                        <h2 className='age-modal__title'>Welcome!</h2>
                        <p className='age-modal__subtitle'>Please confirm your age</p>

                        <div className="age-modal__description">
                            <p>This website features cocktail recipes and information about alcoholic beverages.</p>
                            <p>To continue, please confirm that you are 18 years old or older.</p>
                        </div>

                        <div className="age-modal__buttons">
                            <button onClick={handleConfirm} className="age-modal__btn age-modal__btn--confirm">
                                I am 18 or older
                            </button>
                            <button onClick={handleReject} className="age-modal__btn age-modal__btn--reject">
                                I am under 18
                            </button>
                        </div>
                    </>
                ) : (
                    // ЕКРАН ВІДМОВИ (якщо натиснули "Under 18")
                    <div className="age-modal__error-state">
                        <h2 className='age-modal__title'>Access Denied</h2>
                        <div className="age-modal__description">
                            <p>Sorry, you must be at least 18 years old to access this site.</p>
                            <p>Access to this content is restricted for underage users.</p>
                        </div>

                    </div>
                )}

                <p className="age-modal__footer">
                    By continuing, you confirm that you are of legal drinking age in your country.
                </p>
            </div>
        </div>
    );
};

export default AgeVerification;