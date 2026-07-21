"""Seed realistic, deterministic local development data."""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    Baby,
    ConsultationSlot,
    ContentItem,
    ContentType,
    Product,
    SlotStatus,
    User,
    UserRole,
)

PRODUCTS = [
    ("Soft Muslin Swaddle", "sleep", 0, 6, "24.99", ["cotton", "breathable"]),
    ("Newborn Diaper Pack", "diapering", 0, 3, "18.50", ["hypoallergenic"]),
    ("Silicone Feeding Set", "feeding", 6, 36, "29.95", ["bpa-free", "washable"]),
    ("Digital Bath Thermometer", "bath", 0, 36, "16.99", ["waterproof", "safety"]),
    ("Wooden Teether Ring", "teething", 3, 18, "12.00", ["natural", "sensory"]),
    ("Portable White Noise Machine", "sleep", 0, 36, "34.99", ["rechargeable"]),
    ("Infant Nasal Aspirator", "health", 0, 24, "21.49", ["gentle", "washable"]),
    ("Baby Nail Care Kit", "grooming", 0, 36, "14.75", ["safety", "travel"]),
    ("Tummy Time Activity Mat", "play", 0, 12, "42.00", ["sensory", "padded"]),
    ("Stacking Cups", "play", 6, 36, "15.99", ["motor-skills", "bpa-free"]),
    ("Sippy Cup Trainer", "feeding", 6, 24, "11.50", ["spill-resistant"]),
    ("Organic Cotton Bib Set", "feeding", 3, 24, "19.99", ["organic", "washable"]),
    ("Corner and Outlet Safety Kit", "safety", 6, 36, "27.50", ["baby-proofing"]),
    ("Board Book Gift Set", "learning", 3, 36, "32.00", ["language", "durable"]),
    ("Lightweight Baby Carrier", "travel", 3, 24, "69.00", ["ergonomic", "adjustable"]),
]

CONTENT_ITEMS = [
    ("rhyme", "Twinkle, Twinkle, Little Star", "twinkle.mp3", 0, 36),
    ("rhyme", "Itsy Bitsy Spider", "itsy-bitsy-spider.mp3", 3, 36),
    ("rhyme", "Row, Row, Row Your Boat", "row-your-boat.mp3", 3, 36),
    ("video", "Gentle Newborn Tummy Time", "newborn-tummy-time", 0, 3),
    ("video", "Supported Sitting Practice", "supported-sitting", 4, 9),
    ("video", "First Foods: Safe Textures", "first-food-textures", 6, 12),
    ("sound", "Calming Ocean Waves", "ocean-waves.mp3", 0, 36),
    ("sound", "Steady White Noise", "white-noise.mp3", 0, 24),
    ("sound", "Soft Rain for Naptime", "soft-rain.mp3", 0, 36),
    ("activity", "High-Contrast Card Play", "high-contrast-cards", 0, 4),
    ("activity", "Reach and Grasp Game", "reach-and-grasp", 3, 8),
    ("activity", "Texture Treasure Basket", "texture-basket", 6, 18),
    ("activity", "Peekaboo Object Permanence", "peekaboo", 6, 18),
    ("activity", "Name the Body Parts", "body-parts", 12, 30),
    ("activity", "Indoor Toddler Obstacle Path", "obstacle-path", 18, 36),
]

PEDIATRICIANS = [
    "Dr. Asha Menon",
    "Dr. Rahul Iyer",
    "Dr. Meera Shah",
    "Dr. Nikhil Rao",
    "Dr. Kavya Patel",
]


def get_or_create_user(session: Session) -> User:
    user = session.scalar(select(User).where(User.email == "parent@example.com"))
    if user is None:
        user = User(
            email="parent@example.com",
            role=UserRole.PARENT,
            hashed_password="$2b$12$developmentOnlyHashNotForProduction",
        )
        session.add(user)
        session.flush()
    return user


def seed() -> None:
    with SessionLocal.begin() as session:
        parent = get_or_create_user(session)
        if session.scalar(select(Baby).where(Baby.name == "Maya")) is None:
            session.add(
                Baby(
                    user_id=parent.id,
                    name="Maya",
                    dob=date(2026, 1, 18),
                    sex="female",
                )
            )

        existing_products = set(session.scalars(select(Product.name)))
        session.add_all(
            Product(
                name=name,
                category=category,
                age_min_months=age_min,
                age_max_months=age_max,
                price=Decimal(price),
                tags=tags,
            )
            for name, category, age_min, age_max, price, tags in PRODUCTS
            if name not in existing_products
        )

        existing_content = set(session.scalars(select(ContentItem.title)))
        session.add_all(
            ContentItem(
                type=ContentType(kind),
                title=title,
                url=f"https://cdn.babycare.local/content/{path}",
                age_min_months=age_min,
                age_max_months=age_max,
            )
            for kind, title, path, age_min, age_max in CONTENT_ITEMS
            if title not in existing_content
        )

        start = datetime(2026, 7, 22, 9, 0, tzinfo=UTC)
        existing_slots = set(session.scalars(select(ConsultationSlot.slot_time)))
        session.add_all(
            ConsultationSlot(
                pediatrician_name=PEDIATRICIANS[index % len(PEDIATRICIANS)],
                slot_time=start + timedelta(hours=index),
                status=SlotStatus.BOOKED if index in {3, 7} else SlotStatus.AVAILABLE,
            )
            for index in range(10)
            if start + timedelta(hours=index) not in existing_slots
        )

    print("Seeded 15 products, 15 content items, and 10 consultation slots.")


if __name__ == "__main__":
    seed()
