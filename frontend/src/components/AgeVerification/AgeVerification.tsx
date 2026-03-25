import React, { useState, useEffect } from 'react';
import './AgeVerification.scss';
import { sendAnalyticsEvent, } from '../../api/cocktailApi';

interface AgeVerificationProps {
    onVerified: () => void;
}

const AgeVerification: React.FC<AgeVerificationProps> = ({ onVerified }) => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {

        const isVerified = localStorage.getItem('ageVerified');
        if (!isVerified) {
            setIsVisible(true);
        }
    }, []);

    const handleConfirm = () => {
        sendAnalyticsEvent({
            event_name: `age_confirmation`,
            age_confirmed: true,
        });
        onVerified();
        localStorage.setItem('ageVerified', 'true');
        setIsVisible(false);
    };

    const handleReject = () => {
        sendAnalyticsEvent({
            event_name: `age_confirmation`,
            age_confirmed: false,
        });
        window.location.href = 'https://www.google.com';
    };

    if (!isVisible) return null;

    return (
        <div className="age-modal">
            <div className="age-modal__content">
                <h2>Are you over 18?</h2>
                <p>
                    This website contains information about alcoholic drinks.
                    Please confirm that you are of legal age to continue.
                </p>
                <div className="age-modal__buttons">
                    <button onClick={handleReject} className="btn-reject">No, I am under 18</button>
                    <button onClick={handleConfirm} className="btn-confirm">Yes, I am 18+</button>
                </div>
            </div>
        </div>
    );
};

export default AgeVerification;