import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { verifyEmail } from '../../api/userProfileApi';

export const RegisterEmailVerification = () => {
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState('Verifying your email, please wait...');

    useEffect(() => {
        const uid = searchParams.get('uid');
        const token = searchParams.get('token');

        if (uid && token) {
            verifyEmail(uid, token)
                .then((data) => {
                    setStatus('success');
                    setMessage(data.detail || 'Email verified successfully! You can come back now to registration page.');
                })
                .catch((err) => {
                    setStatus('error');
                    if (err.message === "400") {
                        setMessage(data.detail || 'Link is invalid.');
                    } else {
                        setMessage(err.message || "Verification failed");
                    }
                });
        } else {
            setStatus('error');
            setMessage("Invalid link: missing UID or Token.");
        }
    }, [searchParams]);

    return (
        <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: 'sans-serif' }}>
            <h2 style={{ color: status === 'error' ? '#ff4d4f' : '#222' }}>
                {status === 'loading' ? 'Email Verification' :
                    status === 'success' ? 'Success!' : 'Verification Error'}
            </h2>

            <p style={{ fontSize: '1.1rem', color: '#555' }}>{message}</p>
        </div>
    );
};