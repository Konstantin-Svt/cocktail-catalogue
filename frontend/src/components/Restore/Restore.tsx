import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ConfirmEmail } from '../Steps/ConfirmEmail/ConfirmEmail';
import { passwordApi } from '../../api/authApi';
import './Restore.scss';
import { ResetPasswordSetNew } from '../ResetPasswordSetNew/ResetPasswordSetNew';
import { WelcomeStep } from '../Steps/WelcomeStep/WelcomeStep';

type Step = 'REQUEST' | 'CHECK_INBOX' | 'SET_NEW' | 'SUCCESS';

export const Restore = () => {
    const [searchParams] = useSearchParams();
    const [email, setEmail] = useState('');
    const [step, setStep] = useState<Step>('REQUEST');
    const [isLoading, setIsLoading] = useState(false);

    const uid = searchParams.get('uid');
    const token = searchParams.get('token');
    useEffect(() => {
        if (uid && token) {
            setStep('SET_NEW');
        }
    }, [uid, token]);


    const handleSendLink = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await passwordApi.requestReset(email);
            setStep('CHECK_INBOX');
        } catch (error: any) {

            console.error("Server Error Details:", error.response?.data);

            const errorMessage = error.response?.data?.detail
                || "Error sending reset link. Please check if email is correct.";
            alert(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePasswordResetSuccess = () => {
        setStep('SUCCESS');
    };

    return (
        <div className="restore">
            <header className="restore__header">
                <Link to="/LogIn" className="restore__back">
                    <span className="restore__back-arrow">←</span> Back to cocktails
                </Link>
            </header>

            <main className={`restore__container ${step === 'CHECK_INBOX' || step === 'SUCCESS' ? 'restore__container--centered' : ''}`}>

                {/* КРОК 1: Введення імейлу */}
                {step === 'REQUEST' && (
                    <>
                        <h1 className="restore__title">Reset your password</h1>
                        <form className="restore__form" onSubmit={handleSendLink}>
                            <div className="restore__field">
                                <label>Enter your email</label>
                                <input
                                    type="email"
                                    placeholder="debbie.baker@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <button
                                type="submit"
                                className={`restore__btn ${email && !isLoading ? 'restore__btn--active' : ''}`}
                                disabled={!email || isLoading}
                            >
                                {isLoading ? 'Sending...' : 'Send reset link'}
                            </button>
                        </form>
                        <p className="restore__info">You will receive an email with instructions</p>
                    </>
                )}

                {/* КРОК 2: Підтвердження (твій компонент) */}
                {step === 'CHECK_INBOX' && (
                    <ConfirmEmail
                        email={email}
                        isResetMode={true}
                        password=""
                        onConfirmed={() => {
                            // Для ресету просто чекаємо на перехід з пошти, або редиректимо на головну
                            window.location.href = '/';
                        }}
                        onBack={() => setStep('REQUEST')}
                    />
                )}

                {/* КРОК 3: Введення нового пароля */}
                {step === 'SET_NEW' && uid && token && (
                    <ResetPasswordSetNew
                        uid={uid}
                        token={token}
                        onSuccess={handlePasswordResetSuccess}
                    />
                )}

                {/* КРОК 4: Успіх */}
                {step === 'SUCCESS' && (
                    <WelcomeStep />
                )}
            </main>
        </div>
    );
};