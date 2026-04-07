import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { verifyEmailChange } from '../../api/userProfileApi';

export const ConfirmEmailChange = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const uid = searchParams.get('uid');
        const token = searchParams.get('token');

        if (uid && token) {
            verifyEmailChange(uid, token)
                .then(() => {
                    alert("Email successfully updated!");
                    navigate('/profile');
                })
                .catch((err) => {
                    if (err.message === "401") {
                        alert("Please log in first to verify your email.");
                        navigate('/LogIn');
                    } else {
                        alert("Error: " + err.message);
                    }
                })
                .finally(() => setLoading(false));
        }
    }, [searchParams, navigate]);

    return (
        <div style={{ textAlign: 'center', padding: '50px' }}>
            {loading ? <h2>Verifying change...</h2> : <h2>Processing finished.</h2>}
        </div>
    );
};