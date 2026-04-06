import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { registrationApi } from '../../../api/registrationApi';

interface Props {
    onContinue: (data: any) => void;
    onBack?: () => void;
}

export const RegistrationStep: React.FC<Props> = ({ onContinue }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');

    
    const validation = {
        length: password.length >= 10,
        upper: /[A-Z]/.test(password),
        lower: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
    };

    const isFormValid =
        email.includes('@') &&
        firstName.trim().length > 0 && 
        lastName.trim().length > 0 && 
        validation.length &&
        validation.upper &&
        validation.lower &&
        validation.number &&
        /^[A-Za-z0-9]+$/.test(password) && 
        password === confirmPassword;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!isFormValid) return;

        setIsLoading(true);
        try {
           
            await registrationApi.register({
                email,
                password,
                first_name: firstName,
                last_name: lastName
            });

            
            onContinue({ email, password, firstName, lastName });
        } catch (error: any) {

            const backendError = error.response?.data?.email?.[0] ||
                error.response?.data?.detail ||
                "Registration failed";
            alert(backendError);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="signup">
            <main className="signup__container">
                <h1 className="signup__title">Sign up</h1>

                <form className="signup__form" onSubmit={handleSubmit}>
                    <div className="signup__field">
                        <label>Email address</label>
                        <input
                            type="email"
                            placeholder="debbie.baker@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="signup__field">
                        <label>First Name</label>
                        <input
                            type="text"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            placeholder="Enter your name"
                            required
                        />
                    </div>

                    <div className="signup__field">
                        <label>Last Name</label>
                        <input
                            type="text"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            placeholder="Enter your surname"
                            required
                        />
                    </div>
                    <div className="signup__field">
                        <label>Create a password</label>
                        <div className="signup__password-wrapper">
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="Asstresxvnm99"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                            <button
                                type="button"
                                className="signup__eye-icon"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? '👁️' : '🙈'}
                            </button>
                        </div>
                    </div>

                    <div className="signup__field">
                        <label>Confirm password</label>
                        <input
                            type={showPassword ? "text" : "password"}
                            placeholder="Asstresxvnm99"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>

                    <ul className="registration-requirements">
                        <li className={validation.length ? 'passed' : ''}>
                            <span className="check-mark">
                                <span className="check-mark__v">✓</span>
                            </span>
                            10 characters or more
                        </li>
                        <li className={validation.upper ? 'passed' : ''}>
                            <span className="check-mark">
                                <span className="check-mark__v">✓</span>
                            </span>
                            1 uppercase letter
                        </li>
                        <li className={validation.lower ? 'passed' : ''}>
                            <span className="check-mark">
                                <span className="check-mark__v">✓</span>
                            </span>
                            1 lowercase letter
                        </li>
                        <li className={validation.number ? 'passed' : ''}>
                            <span className="check-mark">
                                <span className="check-mark__v">✓</span>
                            </span>
                            1 number
                        </li>
                    </ul>

                    <button
                        type="submit"
                        className={`signup__btn-continue ${isFormValid && !isLoading ? 'signup__btn-continue--active' : ''}`}
                        disabled={!isFormValid || isLoading}
                    >
                        {isLoading ? 'Sending...' : 'Continue'}
                    </button>
                </form>

                <p className="signup__login-link">
                    Already have an account? <Link to="/login">Log in</Link>
                </p>
            </main>
        </div>
    );
};