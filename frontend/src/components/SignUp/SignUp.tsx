import { Link } from 'react-router-dom';
import './SignUp.scss';
import { useState } from 'react';

export const SignUp = () => {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const validation = {
        length: password.length >= 10,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
    };

    const isFormValid = Object.values(validation).every(Boolean) &&
        password === confirmPassword &&
        password !== '';

    return (
        <div className="signup">
            <header className="signup__header">
                <Link to="/" className="signup__back">
                    <span className="signup__back-arrow">←</span> Back to cocktails
                </Link>
            </header>

            <main className="signup__container">
                <h1 className="signup__title">Sign up</h1>

                <form className="signup__form" onSubmit={(e) => e.preventDefault()}>
                    <div className="signup__field">
                        <label>Email address</label>
                        <input type="email" placeholder="tim.jennings@example.com" />
                    </div>

                    <div className="signup__field">
                        <label>Create a password</label>
                        <div className="signup__password-wrapper">
                            <input
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••••••••"
                            />
                            <button
                                type="button"
                                className={`signup__eye-icon ${showPassword ? 'signup__eye-icon--visible' : ''}`}
                                onClick={() => setShowPassword(!showPassword)}
                            />
                        </div>
                    </div>

                    <div className="signup__field">
                        <label>Confirm password</label>
                        <div className="signup__password-wrapper">
                            <input
                                type={showPassword ? "text" : "password"}
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                placeholder="••••••••••••••"
                            />
                        </div>
                    </div>

                    <ul className="signup__requirements">
                        <li className={`signup__requirement ${validation.length ? 'signup__requirement--passed' : ''}`}>
                            <span className="signup__check">{validation.length ? '✓' : ''}</span>
                            10 characters or more
                        </li>
                        <li className={`signup__requirement ${validation.uppercase ? 'signup__requirement--passed' : ''}`}>
                            <span className="signup__check">{validation.uppercase ? '✓' : ''}</span>
                            1 uppercase letter
                        </li>
                        <li className={`signup__requirement ${validation.lowercase ? 'signup__requirement--passed' : ''}`}>
                            <span className="signup__check">{validation.lowercase ? '✓' : ''}</span>
                            1 lowercase letter
                        </li>
                        <li className={`signup__requirement ${validation.number ? 'signup__requirement--passed' : ''}`}>
                            <span className="signup__check">{validation.number ? '✓' : ''}</span>
                            1 number
                        </li>
                    </ul>

                    <button
                        type="submit"
                        className={`signup__btn-continue ${isFormValid ? 'signup__btn-continue--active' : ''}`}
                        disabled={!isFormValid}
                    >
                        Continue
                    </button>
                </form>

                <p className="signup__login-link">
                    Already have an account? <Link to="/LogIn">Log in</Link>
                </p>

                <div className="signup__divider">
                    <span>or</span>
                </div>

                <div className="signup__socials">
                    <button className="signup__social-btn">
                        <img src="/icons/google.svg" alt="" /> Google
                    </button>
                    <button className="signup__social-btn">
                        <img src="/icons/facebook.svg" alt="" /> Facebook
                    </button>
                </div>
            </main>
        </div>
    );
};