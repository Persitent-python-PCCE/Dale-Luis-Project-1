from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def init_rate_limiter(app):
    """Attach limits to the Flask application.

    Set RATELIMIT_STORAGE_URI to a shared backend such as Redis in production;
    the in-memory fallback is suitable only for local single-process use.
    """
    app.config.setdefault(
        "RATELIMIT_STORAGE_URI",
        os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
    )
    limiter.init_app(app)