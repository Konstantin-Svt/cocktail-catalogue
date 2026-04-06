import React, { useState, useEffect } from 'react';
import './ConfirmEmail.scss';
import axios from 'axios';
import { authApi } from '../../../api/authApi'; // Імпортуй свій створений api файл

interface Props {
    email: string;
    password: string;
    onConfirmed: () => void;
    onBack: () => void; // Додаємо цей пропс
}

export const ConfirmEmail: React.FC<Props> = ({ email, password, onConfirmed, onBack }) => {
    const [timer, setTimer] = useState(30);
    const [isLoading, setIsLoading] = useState(false);

    const handleConfirmClick = async () => {
        setIsLoading(true);
        try {
            const data = await authApi.login({ email, password });

            if (data.access) {
                onConfirmed();
            }
        } catch (error: any) {
            console.error("Login error:", error.response?.data);
            alert("Email not confirmed yet. Please click the link in the email we sent you.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleResend = async () => {
        try {
            await axios.post('/api/user/verify-email-resend/', { email });
            alert("Verification link sent again!");
            setTimer(30);
        } catch (error: any) {
            alert("Failed to resend: " + (error.response?.data?.detail || "Try again later"));
        }
    };

    useEffect(() => {
        const interval = setInterval(() => {
            setTimer((prev) => (prev > 0 ? prev - 1 : 0));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="signup">
            <main className="confirm-email">
                <div className="confirm-email__icon" />
                <h2 className="confirm-email__title">Confirm email address</h2>
                <p className="confirm-email__subtitle">
                    We've sent a verification link to your email.<br />
                    Please check your inbox.
                </p>

                <div className="confirm-email__email-display">
                    <div className="confirm-email__line"></div>
                    <p className="confirm-email__label">Your email</p>
                    <p className="confirm-email__value">{email}</p>
                </div>

                <button
                    onClick={handleConfirmClick}
                    disabled={isLoading}
                    className={`signup__btn-continue ${isLoading ? '' : 'signup__btn-continue--active'}`}
                >
                    {isLoading ? 'Checking...' : "I've confirmed email"}
                </button>

                <button
                    className="confirm-email__resend-btn"
                    disabled={timer > 0 || isLoading}
                    onClick={handleResend}
                >
                    {timer > 0 ? `Resend code in ${timer}s` : 'Resend code'}
                </button>

                <div className="confirm-email__footer">
                    Wrong email? <button onClick={onBack}>Change it</button>
                </div>
            </main>
        </div>
    );
};