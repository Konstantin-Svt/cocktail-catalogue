import React, { useState } from 'react';
import './ResetPasswordSetNew.scss';
import { passwordApi } from '../../api/authApi';

interface Props {
    uid: string;
    token: string;
    onSuccess: () => void;
}

export const ResetPasswordSetNew: React.FC<Props> = ({ uid, token, onSuccess }) => {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);


    const hasMinLength = password.length >= 10;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const passwordsMatch = password === confirmPassword && password !== '';

    const isFormValid = hasMinLength && hasUppercase && hasLowercase && hasNumber && passwordsMatch;

    const handleSave = async () => {
        if (!isFormValid) return;
        setLoading(true);
        try {
            await passwordApi.confirmReset({
                uid,
                token,
                new_password: password
            });
            onSuccess();
        } catch (err: any) {
            alert(err.response?.data?.detail || "Link expired or invalid.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="reset-step">
            <h1 className="reset-step__title">Reset your password</h1>

            <div className="reset-step__field">
                <label>Create a password</label>
                <div className="reset-step__input-wrapper">
                    <input
                        type={showPassword ? "text" : "password"}
                        placeholder="At least 10 characters"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="reset-step__input"
                    />
                    <button
                        className="reset-step__toggle-pass"
                        onClick={() => setShowPassword(!showPassword)}
                    >
                        {showPassword ? '👁️' : '🙈'}
                    </button>
                </div>
            </div>

            <div className="reset-step__field">
                <label>Confirm password</label>
                <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Repeat your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="reset-step__input"
                />
            </div>

            <ul className="reset-step__requirements">
                <li className={hasMinLength ? 'valid' : ''}>10 characters or more</li>
                <li className={hasUppercase ? 'valid' : ''}>1 uppercase letter</li>
                <li className={hasLowercase ? 'valid' : ''}>1 lowercase letter</li>
                <li className={hasNumber ? 'valid' : ''}>1 number</li>
            </ul>

            <button
                className="reset-step__submit-btn"
                disabled={!isFormValid || loading}
                onClick={handleSave}
            >
                {loading ? 'Saving...' : 'Save new password'}
            </button>
        </div>
    );
};