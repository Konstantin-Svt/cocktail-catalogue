import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Profile.scss';
import { fetchUserProfile, requestEmailChange, logoutRequest } from '../../api/userProfileApi';
import { ConfirmEmail } from '../Steps/ConfirmEmail/ConfirmEmail';

export const Profile = () => {
    const [user, setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [isEditingEmail, setIsEditingEmail] = useState(false);
    const [newEmail, setNewEmail] = useState('');
    const [showConfirmScreen, setShowConfirmScreen] = useState(false);
    const [confirmPassword, setConfirmPassword] = useState('');

    const handleEmailChange = async () => {
        if (!newEmail || !confirmPassword) {
            alert("Please fill in both new email and your current password");
            return;
        }

        try {
            
            await requestEmailChange(newEmail, confirmPassword);

            setShowConfirmScreen(true);
            setIsEditingEmail(false);
        } catch (err: any) {
            setConfirmPassword('');
            if (err.message === "401") {
                navigate('/LogIn');
            } else {
                alert(err.message || "Помилка при зміні пошти");
            }
        }
    };

    const navigate = useNavigate();

    useEffect(() => {
        const getProfile = async () => {
            try {
                const data = await fetchUserProfile();
                setUser(data);
            } catch (err: any) {
                console.error("Profile error:", err);
                if (err.message === "401" || err.message?.includes('401')) {
                    navigate('/LogIn');
                }
            } finally {
                setLoading(false);
            }
        };
        getProfile();
    }, [navigate]);

    if (loading) return <div className="profile-loading">Loading...</div>;
    if (!user) return null;

    if (showConfirmScreen) {
        return (
            <ConfirmEmail
                email={newEmail}
                password={confirmPassword}
                isChangeMode={true}
                onConfirmed={() => {
                    setShowConfirmScreen(false);
                    setConfirmPassword('');
                    window.location.reload();
                }}
                onBack={() => {
                    setShowConfirmScreen(false);
                    setConfirmPassword('');
                }}
            />
        );
    }
    return (
        <div className="profile">
            <header className="profile__header">
                <Link to="/" className="profile__back">
                    <span className="profile__back-icon">←</span> Back to cocktails
                </Link>
            </header>

            <main className="profile__content">
                <h1 className="profile__title">My account</h1>

                {/* Основна картка юзера */}
                <section className="profile__section profile__user-card">
                    <div className="profile__avatar-container">
                        <div
                            className="profile__avatar"
                            style={user.avatar ? { backgroundImage: `url(${user.avatar})` } : {}}
                        ></div>
                        
                    </div>
                    <div className="profile__user-info">
                        <h2 className="profile__user-name">{user.first_name} {user.last_name}</h2>
                        <p className="profile__user-email">{user.email}</p>
                    </div>
                </section>

                {/* Блок Basic Information */}
                <section className="profile__section">
                    <div className="profile__section-header">
                        <h3 className="profile__section-title">Basic information</h3>
                    </div>
                    <div className="profile__info-table">
                        <div className="profile__info-row">
                            <span className="profile__info-label">Full Name</span>
                            <span className="profile__info-value">{user.first_name} {user.last_name}</span>
                        </div>
                        <div className="profile__info-row">
                            <span className="profile__info-label">Gender</span>
                            <span className="profile__info-value">{user.gender || 'Female'}</span>
                        </div>
                        <div className="profile__info-row">
                            <span className="profile__info-label">Country</span>
                            <span className="profile__info-value">{user.country || 'Ukraine'}</span>
                        </div>
                    </div>
                </section>

                {/* Блок Account Information */}
                <section className="profile__section">
                    <h3 className="profile__section-title profile__section-title--margin">Account Information</h3>

                    <div className="profile__action-card">
                        <div className="profile__action-content">
                            <span className="profile__info-label">Password</span>
                            <span className="profile__info-value">**********</span>
                        </div>
                        
                        <button className="profile__edit-btn" onClick={() => navigate('/ChangePassword')}>
                            Edit
                        </button>
                    </div>

                    <div className="profile__action-card">
                        <div className="profile__action-icon profile__action-icon-email">
                        </div>
                        <div className="profile__action-content">
                            <span className="profile__info-label">Email <span className='profile---email'>{user.email}</span></span>
                            {isEditingEmail && (
                                <div className="profile__edit-fields">
                                    <input
                                        type="email"
                                        value={newEmail}
                                        onChange={(e) => setNewEmail(e.target.value)}
                                        placeholder="New email address"
                                        className="profile__input"
                                    />
                                    <input
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="Confirm with your password"
                                        className="profile__input"
                                        style={{ marginTop: '10px' }}
                                    />
                                </div>
                            )}
                        </div>
                        <button
                            className="profile__edit-btn"
                            onClick={() => isEditingEmail ? handleEmailChange() : setIsEditingEmail(true)}
                        >
                            {isEditingEmail ? 'Save' : 'Edit'}
                        </button>
                    </div>

                    <div className="profile__action-card profile__action-card--delete">
                        <div className="profile__action-icon profile__action-icon-delete">
                           
                        </div>
                        <div className="profile__action-content">
                            <span className="profile__info-label">Delete account</span>
                            <span className="profile__info-subtext">You'll lose your saved cocktails</span>
                        </div>
                    </div>
                </section>

                <button
                    className="profile__logout-btn"
                    onClick={() => {
                        logoutRequest();
                        localStorage.removeItem('refresh_token');
                        localStorage.removeItem('access_token');
                        window.location.href = '#/LogIn';
                    }}
                >
                    Log Out
                </button>
            </main>
        </div>
    );
};