import { useState } from 'react';
import './SignUp.scss';
import { RegistrationStep } from '../Steps/RegistrationStep/RegistrationStep';
import { ConfirmEmail } from '../Steps/ConfirmEmail/ConfirmEmail';
import { WelcomeStep } from '../Steps/WelcomeStep/WelcomeStep';

export const SignUp = () => {
    const [step, setStep] = useState(1); 
    const [regData, setRegData] = useState({
        email: '',
        password: '',
        first_name: '',
        last_name: ''
    });


    const handleFirstStep = (data: any) => {
        setRegData(data);
        setStep(2);
    };

    const handleBack = () => {
        if (step === 1) {
            window.history.back();
        } else {
            setStep(step - 1);
        }
    };

    return (
        <div className="signup">
            <header className="signup__header">
                <button onClick={handleBack} className="signup__back">
                    <span className="signup__back-arrow">←</span> Back to cocktails
                </button>
            </header>
            {step === 1 && <RegistrationStep
                onContinue={handleFirstStep}
                onBack={() => window.history.back()}
            />}
            {step === 2 && (
                <ConfirmEmail
                    email={regData.email}
                    password={regData.password}
                    onConfirmed={() => setStep(3)}
                    onBack={() => setStep(1)}
                />
            )}
            {step === 3 && <WelcomeStep />}
        </div>
    );
};