import React, { useState, useEffect } from 'react';
import './ConfirmEmail.scss';
import { authApi, passwordApi } from '../../../api/authApi'; 

interface Props {
    email: string;
    password?: string; 
    onConfirmed: () => void;
    onBack: () => void;
    isResetMode?: boolean; 
}

export const ConfirmEmail: React.FC<Props> = ({ email,
    password = '',
    onConfirmed,
    onBack,
    isResetMode = false }) => {
    const [timer, setTimer] = useState(30);
    const [isLoading, setIsLoading] = useState(false);

    const handleConfirmClick = async () => {
        if (isResetMode) {
            alert("Please check your email and click the link to set a new password.");
            return;
        }

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
        setIsLoading(true);
        try {
            if (isResetMode) {
  
                await passwordApi.requestReset(email);
            } else {
                
                await authApi.resendVerification(email);
            }
            alert("Link sent again!");
            setTimer(30);
        } catch (error: any) {
            alert("Failed to resend: " + (error.response?.data?.detail || "Try again later"));
        } finally {
            setIsLoading(false);
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
                <h2 className="confirm-email__title">{isResetMode ? "Check your inbox" : "Confirm email address"}</h2>
                <p className="confirm-email__subtitle">
                    {isResetMode
                        ? "We've sent a password reset link to your email."
                        : "We've sent a verification link to your email."
                    }<br />
                    Please check your inbox.
                </p>

                <div className="confirm-email__email-display">
                    <div className="confirm-email__line"></div>
                    <p className="confirm-email__label">Your email</p>
                    <p className="confirm-email__value">{email}</p>
                </div>
                
                {!isResetMode && (
                    <button
                        onClick={handleConfirmClick}
                        disabled={isLoading}
                        className={`signup__btn-continue ${isLoading ? '' : 'signup__btn-continue--active'}`}
                    >
                        {isLoading ? 'Checking...' : "I've confirmed email"}
                    </button>
                )}

                <button
                    className="confirm-email__resend-btn"
                    disabled={timer > 0 || isLoading}
                    onClick={handleResend}
                >
                    {timer > 0 ? `Resend code in ${timer}s` : 'Resend code'}
                </button>

                <div className="confirm-email__footer">
                    {isResetMode ? "Incorrect email?" : "Wrong email?"} <button onClick={onBack}>Change it</button>
                </div>
            </main>
        </div>
    );
};