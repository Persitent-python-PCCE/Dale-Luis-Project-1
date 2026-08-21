import uuid
from datetime import datetime
from models.payment import Payment

class PaymentService:

    def __init__(self,payment_dao,booking_dao):
        self.payment_dao = payment_dao
        self.booking_dao = booking_dao

    def process_payment(self,booking_id,payment_method="MOCK",result="SUCCESS"):
        booking = self.booking_dao.get_by_id(booking_id)

        if booking is None:
            raise ValueError("Booking not found")

        if booking.status != "PENDING":
            raise ValueError("Booking is not pending")

        existing_payment = self.payment_dao.get_by_booking(booking_id)

        if existing_payment:
            raise ValueError("Payment already exists")

        transaction_id = ("MOCK-" +uuid.uuid4().hex[:12].upper())

        if result == "FAILED":
            payment = Payment(
                booking_id=booking.id,
                transaction_id=transaction_id,
                payment_method=payment_method,
                amount=booking.final_amount,
                status="FAILED"
            )

            self.payment_dao.save(payment)

            return payment

        if result != "SUCCESS":
            raise ValueError("Invalid payment result")

        payment = Payment(
            booking_id=booking.id,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=booking.final_amount,
            status="SUCCESS",
            paid_at=datetime.utcnow()
        )

        return self.payment_dao.save_and_confirm_booking(payment, booking)


    def get_payment(self, id):
        payment = self.payment_dao.get_by_id(id)

        if payment is None:
            raise ValueError("Payment not found")

        return payment

    def get_booking_payment(self, id):
        payment = self.payment_dao.get_by_booking(id)

        if payment is None:
            raise ValueError("Payment not found")

        return payment

    def refund_payment(self,id):
        payment = self.get_payment(id)

        if payment.status != "SUCCESS":
            raise ValueError("Only successful payments can be refunded")

        if payment.refund_status == "COMPLETED":
            raise ValueError("Payment already refunded")

        booking = self.booking_dao.get_by_id(payment.booking_id)

        if booking is None:
            raise ValueError("Booking not found")

        return self.payment_dao.complete_refund_and_cancel_booking(payment, booking)
