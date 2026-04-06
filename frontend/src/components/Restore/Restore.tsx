import { useState } from 'react';
import { Link } from 'react-router-dom';
import './Restore.scss';

export const Restore = () => {
    const [email, setEmail] = useState('');
    const [isSubmitted, setIsSubmitted] = useState(false);

    const handleSendLink = (e: React) => {
        e.preventDefault();
        // Тут буде логіка виклику API
        setIsSubmitted(true);
    };

    if (isSubmitted) {
        return <CheckInbox email={email} />;
    }

    return (
        <div className="restore">
            <header className="restore__header">
                <Link to="/LogIn" className="restore__back">
                    <span className="restore__back-arrow">←</span> Back to cocktails
                </Link>
            </header>

            <main className="restore__container">
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
                        className={`restore__btn ${email ? 'restore__btn--active' : ''}`}
                        disabled={!email}
                    >
                        Send reset link
                    </button>
                </form>

                <p className="restore__info">
                    You will receive an email with instructions
                </p>
            </main>
        </div>
    );
};

// Внутрішній компонент для стану "Check your inbox"
const CheckInbox = ({ email }: { email: string }) => (
    <div className="restore">
        <header className="restore__header">
            <Link to="/LogIn" className="restore__back">
                <span className="restore__back-arrow">←</span> Back to cocktails
            </Link>
        </header>

        <main className="restore__container restore__container--centered">

            <div className="restore__icon-bg"></div>

            <h1 className="restore__title">Check your inbox</h1>
            <p className="restore__subtitle">
                Your email: <strong>{email || 'tim.jennings@example.com'}</strong>
            </p>
            <p className="restore__description">
                We've sent you a link to reset your password
            </p>

            <button className="restore__btn restore__btn--active">
                Confirm your email address
            </button>

            <p className="restore__resend">
                Didn't receive the email? <button onClick={() => { }}>Resend confirmation</button>
            </p>
        </main>
    </div>
);