import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\d{10}$")


def validate_email(email):
    if not email or not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
        raise ValueError("Invalid email format")
    return email.strip()


def validate_phone(phone):
    if phone is not None:
        phone_str = str(phone).strip()
        if phone_str:
            if not PHONE_REGEX.match(phone_str):
                raise ValueError("Phone number must be exactly 10 digits")
            return phone_str
    return None
