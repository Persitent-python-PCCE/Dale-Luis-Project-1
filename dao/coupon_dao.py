from models.coupon import Coupon
from config.database import db
from datetime import datetime


class CouponDAO:

    def get_all(self):
        return Coupon.query.all()

    def get_by_id(self, coupon_id):
        return Coupon.query.get(coupon_id)

    def get_by_code(self, code):
        return Coupon.query.filter_by(
            code=code
        ).first()

    def get_active_coupon(self, code):
        now = datetime.utcnow()

        return Coupon.query.filter(
            Coupon.code == code,
            Coupon.is_active == True,
            Coupon.valid_from <= now,
            Coupon.valid_until >= now,
            Coupon.used_count < Coupon.usage_limit
        ).first()

    def save(self, coupon):
        db.session.add(coupon)
        db.session.commit()
        return coupon

    def update(self, coupon):
        db.session.commit()
        return coupon

    def deactivate(self, coupon):
        coupon.is_active = False
        db.session.commit()
        return coupon

    def increment_usage(self, coupon):
        coupon.used_count += 1
        db.session.commit()
        return coupon