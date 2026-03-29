import { Link } from 'react-router-dom';
import { useState } from 'react';
import './LogIn.scss';

export const LogIn = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const isFormValid = email.length > 0 && password.length > 0;

    return (
        <div className="login">
            <header className="login__header">
                <Link to="/" className="login__back">
                    <span className="login__back-arrow">←</span> Back to cocktails
                </Link>
            </header>

            <main className="login__container">
                <h1 className="login__title">Log in</h1>

                <form className="login__form" onSubmit={(e) => e.preventDefault()}>
                    <div className="login__field">
                        <label>Email address</label>
                        <input
                            type="email"
                            placeholder="debbie.baker@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>

                    <div className="login__field">
                        <label>Password</label>
                        <div className="login__password-wrapper">
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="Asstresxvnm99"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                            <button
                                type="button"
                                className={`login__eye-icon ${showPassword ? 'login__eye-icon--visible' : ''}`}
                                onClick={() => setShowPassword(!showPassword)}
                            />
                        </div>
                        <div className="login__restore-link">
                            Forgot your password? <Link to="/restore">Restore</Link>
                        </div>
                    </div>

                    <button
                        type="submit"
                        className={`login__btn-continue ${isFormValid ? 'login__btn-continue--active' : ''}`}
                        disabled={!isFormValid}
                    >
                        Continue
                    </button>
                </form>

                <p className="login__signup-link">
                    Don't have an account? <Link to="/SignUp">Registration</Link>
                </p>

                <div className="login__divider">
                    <span>or</span>
                </div>

                <div className="login__socials">
                    <button className="login__social-btn">
                        <img src="/icons/google.svg" alt="" /> Google
                    </button>
                    <button className="login__social-btn">
                        <img src="/icons/facebook.svg" alt="" /> Facebook
                    </button>
                </div>
            </main>
        </div>
    );
};