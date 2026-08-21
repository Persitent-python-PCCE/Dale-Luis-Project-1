from models.review import Review


class ReviewService:

    def __init__(self, review_dao):
        self.review_dao = review_dao

    def get_event_reviews(self, event_id):
        return self.review_dao.get_by_event(event_id)

    def get_user_reviews(self, user_id):
        return self.review_dao.get_by_user(user_id)

    def create_review(
        self, user_id, event_id, booking_id, rating, review_text):

        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        existing = self.review_dao.get_user_event_review(user_id,event_id)

        if existing:
            raise ValueError("You have already reviewed this event")

        review = Review(
            user_id=user_id,
            event_id=event_id,
            booking_id=booking_id,
            rating=rating,
            review_text=review_text,
        )

        return self.review_dao.save(review)

    def update_review(self, id, user_id, rating, review_text):
        review = self.review_dao.get_by_id(id)

        if review is None:
            raise ValueError("Review not found")

        if review.user_id != user_id:
            raise ValueError("You cannot edit this review")

        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        review.rating = rating
        review.review_text = review_text

        return self.review_dao.update(review)

    def delete_review(self,id,user_id):
        review = self.review_dao.get_by_id(id)

        if review is None:
            raise ValueError("Review not found")

        if review.user_id != user_id:
            raise ValueError("You cannot delete this review")

        self.review_dao.delete(review)
