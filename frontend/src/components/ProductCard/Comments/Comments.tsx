import React, { useState, useEffect } from 'react';
import { fetchComments, postComment } from '../../../api/cocktailApi';
import './Comments.scss';

const STAR_ICON = '/img/star.svg';
const DEFAULT_AVATAR = '/img/default-avatar.svg';


interface Comment {
    id: number;
    user_id: number; // Тепер приходить id юзера напряму
    text: string;
    mark: number | null;
    timestamp: string;
    user: {
        id: number;
        username: string; // Додаємо username
        first_name: string;
        last_name: string
    };

    created_at: string;
}

export const Comments: React.FC<{
    cocktailId: string;
    initialComments: any[]; }> = ({ cocktailId, initialComments }) => {
        const [comments, setComments] = useState<Comment[]>(initialComments);
    const [newComment, setNewComment] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [rating, setRating] = useState(0);
    const charLimit = 300;

    useEffect(() => {
    // Тільки синхронізація з пропсами від ProductCard
    setComments(initialComments);
}, [initialComments]);

    const loadComments = async () => {
        try {
            const data = await fetchComments(cocktailId);
            // data вже буде масивом, бо ми зробили це в cocktailApi.ts
            setComments(data);
        } catch (err) {
            console.error("Помилка завантаження:", err);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (newComment.length < 5) {
            alert("Minimum 5 characters required");
            return;
        }
        if (rating === 0) {
            alert("Please select a rating");
            return;
        }

        setIsSubmitting(true);
        try {
            await postComment(cocktailId, newComment, rating);
            setNewComment('');

            // ЧЕКАЄМО 1 СЕКУНДУ, щоб бекенд прокинувся
            setTimeout(() => {
                loadComments();
            }, 1000);

        } catch (err: any) {
            alert(err.message);
        }
    };

    return (
        <div className="comments-section">
            <h2 className="comments-section__title">Write a review</h2>

            <form className="comments-section__form" onSubmit={handleSubmit}>
                <div className="comments-section__form-content">
                    {/* 1. Ряд: Аватар та Зірки */}
                    <div className="comments-section__user-row">
                        <div className="comments-section__user-avatar" />
                        <div className="comments-section__rating-select">
                            {[1, 2, 3, 4, 5].map((star) => (
                                <div
                                    key={star}
                                    className={`star-selectable ${star <= rating ? 'active' : ''}`}
                                    onClick={() => setRating(star)}
                                />
                            ))}
                        </div>
                    </div>

                    {/* 2. Ряд: Textarea */}
                    <textarea
                        className="comments-section__field"
                        placeholder="Drop your taste thoughts"
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        maxLength={charLimit}
                    />

                    {/* 3. Ряд: Лічильник */}
                    <div className="comments-section__char-count">
                        {newComment.length}/{charLimit}
                    </div>

                    {/* 4. Ряд: Кнопка */}
                    <button
                        type="submit"
                        className="comments-section__submit"
                        disabled={isSubmitting || !newComment.trim()}
                    >
                        {isSubmitting ? 'Sending...' : 'Post review'}
                    </button>
                </div>
            </form>
            <div className="comments-section__block">
                <h2 className="comments-section__title">Reviews</h2>
                <div className="comments-section__rate-card">
                    <div className="rate-stats">
                        {[5, 4, 3, 2, 1].map((num) => (
                            <div key={num} className="rate-stats__row">
                                <span className="rate-stats__num">{num}</span>
                                <div className="rate-stats__progress">
                                    <div className="rate-stats__fill" style={{ width: num === 5 ? '85%' : num === 4 ? '15%' : '5%' }} />
                                </div>
                                <span className="rate-stats__count">{num === 5 ? '17' : num === 4 ? '3' : '1'}</span>
                            </div>
                        ))}
                    </div>

                    <div className="rate-summary">
                        <div className="rate-summary__value">4.8</div>
                        <div className="rate-summary__stars">★★★★★</div>
                        <div className="rate-summary__total">Reviews: {comments.length}</div>
                    </div>
                </div>
            </div>
            
        </div>
    );
};