from models.payment import Payment
from config.database import db
from datetime import datetime


class PaymentDAO:

    def get_all(self):
        return Payment.query.all()

    def get_by_id(self, payment_id):
        return Payment.query.get(payment_id)

    def get_by_booking(self, booking_id):
        return Payment.query.filter_by(
            booking_id=booking_id
        ).first()

    def get_by_transaction(self, transaction_id):
        return Payment.query.filter_by(
            transaction_id=transaction_id
        ).first()

    def save(self, payment):
        db.session.add(payment)
        db.session.commit()
        return payment

    def save_and_confirm_booking(self, payment, booking):
        try:
            db.session.add(payment)
            booking.status = "CONFIRMED"
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return payment

    def update(self, payment):
        db.session.commit()
        return payment

    def update_refund_status(
        self,
        payment,
        status,
        refund_amount=None
    ):
        payment.refund_status = status

        if refund_amount is not None:
            payment.refund_amount = refund_amount

        if status == "COMPLETED":
            payment.refunded_at = datetime.utcnow()

        db.session.commit()

        return payment

    def complete_refund_and_cancel_booking(self, payment, booking):
        try:
            payment.refund_status = "COMPLETED"
            payment.refund_amount = payment.amount
            payment.refunded_at = datetime.utcnow()
            booking.status = "CANCELLED"
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return payment
