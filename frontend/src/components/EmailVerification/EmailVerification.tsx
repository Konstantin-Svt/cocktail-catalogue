import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { verifyEmailChange } from '../../api/userProfileApi';

export const EmailVerification = () => {
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState('Verifying your email, please wait...');
    const navigate = useNavigate();

    useEffect(() => {
        const uid = searchParams.get('uid');
        const token = searchParams.get('token');

        if (uid && token) {
            verifyEmailChange(uid, token)
                .then((data) => {
                    setStatus('success');
                    setMessage(data.detail || 'Email changed successfully!');
                    // Редирект у профіль, бо пошта вже змінена
                    setTimeout(() => navigate('/profile'), 3000);
                })
                .catch((err) => {
                    setStatus('error');
                    if (err.message === "401") {
                        setMessage("Please log in first to confirm email change.");
                        setTimeout(() => navigate('/LogIn'), 3000);
                    } else {
                        setMessage(err.message || "Verification failed");
                    }
                });
        } else {
            setStatus('error');
            setMessage("Invalid link: missing UID or Token.");
        }
    }, [searchParams, navigate]);

    return (
        <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: 'sans-serif' }}>
            <h2 style={{ color: status === 'error' ? '#ff4d4f' : '#222' }}>
                {status === 'loading' ? 'Email Verification' :
                    status === 'success' ? 'Success!' : 'Verification Error'}
            </h2>

            <p style={{ fontSize: '1.1rem', color: '#555' }}>{message}</p>

            {status === 'error' && (
                <button
                    onClick={() => navigate('/LogIn')}
                    style={{ padding: '10px 20px', cursor: 'pointer', marginTop: '20px' }}
                >
                    Go to Login
                </button>
            )}
        </div>
    );
};