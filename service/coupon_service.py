from models.coupon import Coupon

class CouponService:
    def __init__(self, coupon_dao):
        self.coupon_dao = coupon_dao

    def get_all_coupons(self):
        return self.coupon_dao.get_all()

    def get_coupon(self, coupon_id):
        coupon = self.coupon_dao.get_by_id(coupon_id)

        if coupon is None:
            raise ValueError("Coupon not found")

        return coupon

    def create_coupon(self,data,admin_id):
        code = data.get("code")

        if not code:
            raise ValueError("Coupon code is required")
        
        code = code.strip().upper()
        existing = self.coupon_dao.get_by_code(code)

        if existing:
            raise ValueError("Coupon already exists")
        
        discount_type = data.get("discount_type")
        discount_value = data.get("discount_value")
        usage_limit = data.get("usage_limit")
        valid_from = data.get("valid_from")
        valid_until = data.get("valid_until")
        
        if discount_type not in ["PERCENTAGE", "FIXED"]:
            raise ValueError("Invalid discount type")

        if discount_value is None or discount_value <= 0:
            raise ValueError("Discount value must be greater than 0")

        if discount_type == "PERCENTAGE" and discount_value > 100:
            raise ValueError("Percentage discount cannot exceed 100")

        if usage_limit is None or usage_limit <= 0:
            raise ValueError("Usage limit must be greater than 0")

        if valid_from is None or valid_until is None:
            raise ValueError("Coupon validity dates are required")

        if valid_until <= valid_from:
            raise ValueError("Invalid coupon dates")

        coupon = Coupon(
            code=code,
            description=data.get("description"),
            discount_type=data["discount_type"],
            discount_value=data["discount_value"],
            minimum_amount=data.get("minimum_amount", 0),
            maximum_discount=data.get("maximum_discount"),
            usage_limit=data["usage_limit"],
            used_count=0,
            valid_from=valid_from,
            valid_until=valid_until,
            is_active=True,
            created_by=admin_id
        )

        return self.coupon_dao.save(coupon)

    def validate_coupon(self, code, amount):
        if not code:
            raise ValueError("Coupon code is required")

        code = code.strip().upper()

        coupon = self.coupon_dao.get_active_coupon(code)

        if coupon is None:
            raise ValueError("Invalid or expired coupon")

        if amount < coupon.minimum_amount:
            raise ValueError(f"Minimum purchase amount is {coupon.minimum_amount}")

        return coupon

    def calculate_discount(self,coupon,amount):
        if coupon.discount_type == "PERCENTAGE":
            discount = (amount * float(coupon.discount_value)) / 100

            if coupon.maximum_discount:
                discount = min(discount,float(coupon.maximum_discount))

        elif coupon.discount_type == "FIXED":
            discount = float(coupon.discount_value)

        else:
            raise ValueError("Invalid discount type")

        discount = min(discount, amount)

        return discount

    def use_coupon(self,code,amount):
        coupon = self.validate_coupon(code,amount)

        discount = self.calculate_discount(coupon,amount)

        coupon = self.coupon_dao.increment_usage(coupon)

        return {
            "coupon": coupon,
            "discount": discount,
            "final_amount": amount - discount
        }

    def update_coupon(self,coupon_id,data):
        coupon = self.get_coupon(coupon_id)
        
        if "discount_value" in data:
            if data["discount_value"] <= 0:
                raise ValueError("Discount must be greater than 0")
                
            coupon.discount_value = data["discount_value"]

        if "minimum_amount" in data:
            coupon.minimum_amount = data["minimum_amount"]

        if "maximum_discount" in data:
            coupon.maximum_discount = data["maximum_discount"]
                
        if "usage_limit" in data:
            if data["usage_limit"] < coupon.used_count:
                raise ValueError("Usage limit cannot be less than used count")

            coupon.usage_limit = data["usage_limit"]

        if "valid_until" in data:
            coupon.valid_until = data["valid_until"]

        if "description" in data:
            coupon.description = data["description"]

        if "is_active" in data:
            coupon.is_active = data["is_active"]

        return self.coupon_dao.update(coupon)

    def deactivate_coupon(self,coupon_id):
        coupon = self.get_coupon(coupon_id)

        coupon.is_active = False

        return self.coupon_dao.update(coupon)
