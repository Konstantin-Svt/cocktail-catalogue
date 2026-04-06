import React, { useState } from 'react';
import './AlmostThere.scss';

interface Props {
    onFinish: () => void;
    onBack: () => void;
}

export const AlmostThere: React.FC<Props> = ({ onFinish, onBack }) => {
    const [gender, setGender] = useState('female');
    const [firstName, setFirstName] = useState('Brooklyn');
    const [lastName, setLastName] = useState('Simmons');

    const isFormValid = gender && firstName && lastName;

    return (
        <div className="almost-there">
            <h2 className="almost-there__title">Almost there!</h2>
            <p className="almost-there__subtitle">
                Just your name, gender and country — and you're all set!
            </p>

            <form className="almost-there__form" onSubmit={(e) => { e.preventDefault(); onFinish(); }}>
                <div className="almost-there__field">
                    <label>First name</label>
                    <div className="almost-there__input-wrapper">
                        <input
                            type="text"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            className="almost-there__input--active"
                        />
                        {firstName && (
                            <button type="button" className="almost-there__clear" onClick={() => setFirstName('')}>×</button>
                        )}
                    </div>
                </div>

                <div className="almost-there__field">
                    <label>Last name</label>
                    <div className="almost-there__input-wrapper">
                        <input
                            type="text"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            className="almost-there__input--active"
                        />
                        {lastName && (
                            <button type="button" className="almost-there__clear" onClick={() => setLastName('')}>×</button>
                        )}
                    </div>
                </div>

                <div className="almost-there__field">
                    <label>Gender</label>
                    <div className="almost-there__gender-group">
                        <label className="almost-there__gender-option">
                            <input type="radio" name="gender" checked={gender === 'male'} onChange={() => setGender('male')} />
                            <span>Male</span>
                        </label>
                        <label className="almost-there__gender-option">
                            <input type="radio" name="gender" checked={gender === 'female'} onChange={() => setGender('female')} />
                            <span>Female</span>
                        </label>
                    </div>
                </div>

                <div className="almost-there__field">
                    <label>Country</label>
                    <div className="almost-there__select-wrapper">
                        <span className="almost-there__country-code">UA</span>
                        <select className="almost-there__select">
                            <option>Ukraine</option>
                            <option>USA</option>
                        </select>
                    </div>
                </div>

                {/* КНОПКА ПОВЕРНУЛАСЯ */}
                <button
                    type="submit"
                    className={`almost-there__btn-continue ${isFormValid ? 'almost-there__btn-continue--active' : ''}`}
                    disabled={!isFormValid}
                >
                    Continue
                </button>

                <div className="almost-there__footer">
                    Wrong email? <button type="button" onClick={onBack}>Change it</button>
                </div>
            </form>
        </div>
    );
};