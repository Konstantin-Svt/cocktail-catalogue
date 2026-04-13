import { useState } from "react";
import { Link } from "react-router-dom"
import './AuthModal.scss';

interface AuthModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
    // Якщо модалка не має бути відкритою, нічого не рендеримо
    if (!isOpen) return null;

    return (
        <div className="auth-modal-overlay">
            <div className="auth-modal">
                <button className="auth-modal__close" onClick={onClose}>✕</button>
                <div className="heart-icon"></div>
                <h2>Save your favorite cocktails</h2>
                <p>Keep your favorite cocktails and access them anytime</p>

                <Link to="/SignUp" className="btn-signup">Sign up</Link>
                <Link to="/LogIn" className="btn-login">Log in</Link>

                <button className='btn-out' onClick={onClose}>
                    Continue without account
                </button>
            </div>
        </div>
    );
}