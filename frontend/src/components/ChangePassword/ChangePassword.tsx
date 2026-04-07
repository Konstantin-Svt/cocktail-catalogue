import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { updatePassword } from '../../api/userProfileApi';
import './ChangePassword.scss'; 

export const ChangePassword = () => {
    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [repeatPassword, setRepeatPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const passwordRegex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])[A-Za-z0-9]{10,64}$/;
    const isPasswordValid = passwordRegex.test(newPassword);

    const handleSave = async () => {
        if (!isPasswordValid) {
            alert("Password does not meet requirements!");
            return;
        }
        if (newPassword !== repeatPassword) {
            alert("Passwords do not match!");
            return;
        }

        setLoading(true);
        try {
            await updatePassword(oldPassword, newPassword);
            alert("Password changed successfully!");
            navigate('/profile');
        } catch (err: any) {
            alert(err.message || "Failed to change password");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="change-password">
            <header className="change-password__header">
                <Link to="/profile" className="change-password__back">← My account</Link>
            </header>

            <main className="change-password__content">
                <h1 className="change-password__title">Change password</h1>

                <section className="change-password__group">
                    <label>Confirm your current password</label>
                    <input
                        type="password"
                        placeholder="Current password"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                        className="change-password__input"
                    />
                </section>

                <section className="change-password__group">
                    <label>Set a new password</label>
                    <div className="change-password__row">
                        <div className="change-password__field">
                            <input
                                type="password"
                                placeholder="New password"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                className="change-password__input"
                            />
                            <ul className="change-password__hints">
                                <li className={newPassword.length >= 10 ? 'valid' : ''}>10 characters or more</li>
                                <li className={/[A-Z]/.test(newPassword) ? 'valid' : ''}>1 uppercase letter</li>
                                <li className={/[a-z]/.test(newPassword) ? 'valid' : ''}>1 lowercase letter</li>
                                <li className={/[0-9]/.test(newPassword) ? 'valid' : ''}>1 number</li>
                            </ul>
                        </div>

                        <div className="change-password__field">
                            <input
                                type="password"
                                placeholder="Repeat new password"
                                value={repeatPassword}
                                onChange={(e) => setRepeatPassword(e.target.value)}
                                className="change-password__input"
                            />
                        </div>
                    </div>
                </section>

                <div className="change-password__actions">
                    <button className="btn-cancel" onClick={() => navigate('/profile')}>Cancel</button>
                    <button
                        className="btn-save"
                        disabled={loading || !isPasswordValid || newPassword !== repeatPassword}
                        onClick={handleSave}
                    >
                        {loading ? 'Saving...' : 'Save'}
                    </button>
                </div>
            </main>
        </div>
    );
};