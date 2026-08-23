import uuid
from datetime import datetime
from models.payment import Payment
from config.database import db

class PaymentService:

    def __init__(self,payment_dao,booking_dao):
        self.payment_dao = payment_dao
        self.booking_dao = booking_dao

    def process_payment(self,booking_id,payment_method="MOCK",result="SUCCESS"):
        try:
            booking = self.booking_dao.get_and_lock_by_id(booking_id)

            if booking is None:
                raise ValueError("Booking not found")

            if booking.status != "PENDING":
                raise ValueError("Booking is not pending")

            if self.payment_dao.get_and_lock_by_booking(booking_id):
                raise ValueError("Payment already exists")

            if result not in {"SUCCESS", "FAILED"}:
                raise ValueError("Invalid payment result")

            payment = Payment(
                booking_id=booking.id,
                transaction_id="MOCK-" + uuid.uuid4().hex[:12].upper(),
                payment_method=payment_method,
                amount=booking.final_amount,
                status=result,
                paid_at=datetime.utcnow() if result == "SUCCESS" else None,
            )
            db.session.add(payment)
            # Failed payments release the seats for another customer.
            booking.status = "CONFIRMED" if result == "SUCCESS" else "CANCELLED"
            db.session.commit()
            return payment
        except Exception:
            db.session.rollback()
            raise


    def get_payment(self, id):
        payment = self.payment_dao.get_by_id(id)

        if payment is None:
            raise ValueError("Payment not found")

        return payment

    def get_booking(self, booking_id):
        booking = self.booking_dao.get_by_id(booking_id)

        if booking is None:
            raise ValueError("Booking not found")

        return booking

    def get_booking_payment(self, id):
        payment = self.payment_dao.get_by_booking(id)

        if payment is None:
            raise ValueError("Payment not found")

        return payment

    def refund_payment(self,id):
        try:
            payment = self.payment_dao.get_and_lock_by_id(id)

            if payment is None:
                raise ValueError("Payment not found")
            if payment.status != "SUCCESS":
                raise ValueError("Only successful payments can be refunded")
            if payment.refund_status == "COMPLETED":
                raise ValueError("Payment already refunded")

            booking = self.booking_dao.get_and_lock_by_id(payment.booking_id)
            if booking is None:
                raise ValueError("Booking not found")

            payment.refund_status = "COMPLETED"
            payment.refund_amount = payment.amount
            payment.refunded_at = datetime.utcnow()
            booking.status = "CANCELLED"
            db.session.commit()
            return payment
        except Exception:
            db.session.rollback()
            raise
