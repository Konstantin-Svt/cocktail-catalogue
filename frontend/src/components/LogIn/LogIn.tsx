import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import './LogIn.scss';
import { authApi } from '../../api/authApi';

export const LogIn = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const isFormValid = email.length > 0 && password.length > 0;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!isFormValid) return;

        setIsLoading(true);
        setError('');

        try {
            const data = await authApi.login({ email, password });

            if (data.access) {
                navigate('/');
            }
        } catch (err: any) {
            console.error("Login error:", err.response?.data);
            const errorMsg = err.response?.data?.detail || "Invalid email or password";
            setError(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login">
            <header className="login__header">
                <Link to="/" className="login__back">
                    <span className="login__back-arrow">←</span> Back to cocktails
                </Link>
            </header>

            <main className="login__container">
                <h1 className="login__title">Log in</h1>

                <form className="login__form" onSubmit={handleSubmit}>
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
                        {error && <p className="login__error-message" style={{ color: '#FF4D4D', fontSize: '14px', marginTop: '8px' }}>{error}</p>}
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
            </main>
        </div>
    );
};