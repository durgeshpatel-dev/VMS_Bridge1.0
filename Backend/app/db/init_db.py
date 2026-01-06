from __future__ import annotations

from app.db.session import get_engine

# Ensure models are imported so SQLAlchemy knows about them
from app.db import models  # noqa: F401
from app.db.base import Base


def main() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("Created tables (if not exist).")


if __name__ == "__main__":
    main()
