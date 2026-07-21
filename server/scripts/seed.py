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

COMMONS = "https://commons.wikimedia.org/wiki/Special:Redirect/file/"

# URLs and licensing metadata are kept together so media provenance remains auditable.
CONTENT_ITEMS = [
    {
        "type": "rhyme",
        "title": "Twinkle, Twinkle, Little Star",
        "url": f"{COMMONS}Twinkle_Twinkle_Little_Star_plain.ogg",
        "ages": (0, 36),
        "config": {
            "license": "Public domain",
            "author": "CambridgeBayWeather",
            "source_page": "https://commons.wikimedia.org/wiki/File:Twinkle_Twinkle_Little_Star_plain.ogg",
        },
    },
    {
        "type": "rhyme",
        "title": "Itsy Bitsy Spider",
        "url": f"{COMMONS}Itsy_Bitsy_Spider.ogg",
        "ages": (3, 36),
        "config": {
            "license": "CC BY-SA 3.0 / GFDL",
            "author": "Wwaters",
            "source_page": "https://commons.wikimedia.org/wiki/File:Itsy_Bitsy_Spider.ogg",
        },
    },
    {
        "type": "rhyme",
        "title": "Row, Row, Row Your Boat",
        "url": f"{COMMONS}Row%2C_Row%2C_Row_Your_Boat.ogg",
        "ages": (3, 36),
        "config": {
            "license": "CC BY-SA 3.0 / GFDL",
            "author": "CambridgeBayWeather",
            "source_page": "https://commons.wikimedia.org/wiki/File:Row,_Row,_Row_Your_Boat.ogg",
        },
    },
    {
        "type": "rhyme",
        "title": "Mary Had a Little Lamb",
        "url": f"{COMMONS}Mary_Had_a_Little_Lamb.ogg",
        "ages": (3, 36),
        "config": {
            "license": "Public domain",
            "author": "Celestianpower",
            "source_page": "https://commons.wikimedia.org/wiki/File:Mary_Had_a_Little_Lamb.ogg",
        },
    },
    {
        "type": "video",
        "title": "Animal Sounds Song",
        "url": "33UG1Uch05Y",
        "ages": (12, 48),
        "config": {"provider": "youtube", "channel": "Kids TV"},
    },
    {
        "type": "video",
        "title": "Alphabet Song",
        "url": "cE3LzPQgQmk",
        "ages": (18, 60),
        "config": {"provider": "youtube", "channel": "Kids TV"},
    },
    {
        "type": "video",
        "title": "Wheels on the Bus",
        "url": "CeUAFs_KyIc",
        "ages": (12, 48),
        "config": {"provider": "youtube", "channel": "Kids TV"},
    },
    {
        "type": "video",
        "title": "Classic Nursery Rhymes",
        "url": "NVNE19OHfVg",
        "ages": (18, 60),
        "config": {"provider": "youtube", "channel": "Doggyland"},
    },
    {
        "type": "sound",
        "title": "Soft Low Tone",
        "url": "generated://tone/low",
        "ages": (0, 36),
        "config": {
            "generator": "oscillator",
            "waveform": "sine",
            "frequency_hz": 220,
            "duration_ms": 900,
            "gain": 0.15,
        },
    },
    {
        "type": "sound",
        "title": "Soft Middle Tone",
        "url": "generated://tone/middle",
        "ages": (0, 36),
        "config": {
            "generator": "oscillator",
            "waveform": "sine",
            "frequency_hz": 329.63,
            "duration_ms": 900,
            "gain": 0.15,
        },
    },
    {
        "type": "sound",
        "title": "Soft High Tone",
        "url": "generated://tone/high",
        "ages": (0, 36),
        "config": {
            "generator": "oscillator",
            "waveform": "sine",
            "frequency_hz": 440,
            "duration_ms": 900,
            "gain": 0.15,
        },
    },
    {
        "type": "activity",
        "title": "Primary Color Tone Match",
        "url": "game://color-sound/primary",
        "ages": (12, 36),
        "config": {
            "game_type": "color_sound_match",
            "instructions": "Hear a tone, then tap its color.",
            "shuffle": True,
            "pairs": [
                {"id": "red-low", "label": "Red", "color": "#EF4444", "tone_hz": 220},
                {
                    "id": "yellow-mid",
                    "label": "Yellow",
                    "color": "#FACC15",
                    "tone_hz": 329.63,
                },
                {
                    "id": "blue-high",
                    "label": "Blue",
                    "color": "#3B82F6",
                    "tone_hz": 440,
                },
            ],
        },
    },
    {
        "type": "activity",
        "title": "Garden Color Tone Match",
        "url": "game://color-sound/garden",
        "ages": (18, 48),
        "config": {
            "game_type": "color_sound_match",
            "instructions": "Match each garden color to its sound.",
            "shuffle": True,
            "pairs": [
                {
                    "id": "leaf",
                    "label": "Leaf green",
                    "color": "#22C55E",
                    "tone_hz": 261.63,
                },
                {
                    "id": "flower",
                    "label": "Flower pink",
                    "color": "#EC4899",
                    "tone_hz": 349.23,
                },
                {
                    "id": "sky",
                    "label": "Sky blue",
                    "color": "#38BDF8",
                    "tone_hz": 523.25,
                },
            ],
        },
    },
    {
        "type": "activity",
        "title": "Rainbow Color Tone Match",
        "url": "game://color-sound/rainbow",
        "ages": (24, 60),
        "config": {
            "game_type": "color_sound_match",
            "instructions": "Build a rainbow by matching tones from low to high.",
            "shuffle": True,
            "pairs": [
                {
                    "id": "orange",
                    "label": "Orange",
                    "color": "#F97316",
                    "tone_hz": 293.66,
                },
                {"id": "green", "label": "Green", "color": "#16A34A", "tone_hz": 392},
                {
                    "id": "purple",
                    "label": "Purple",
                    "color": "#9333EA",
                    "tone_hz": 493.88,
                },
            ],
        },
    },
    {
        "type": "rhyme",
        "title": "Baa, Baa, Black Sheep",
        "url": f"{COMMONS}Bahbahblacksheep.ogg",
        "ages": (3, 36),
        "config": {
            "license": "CC0 1.0",
            "author": "Rex Sueciae",
            "source_page": "https://commons.wikimedia.org/wiki/File:Bahbahblacksheep.ogg",
        },
    },
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

        existing_content = {
            item.title: item for item in session.scalars(select(ContentItem))
        }
        for data in CONTENT_ITEMS:
            age_min, age_max = data["ages"]
            values = {
                "type": ContentType(data["type"]),
                "url": data["url"],
                "age_min_months": age_min,
                "age_max_months": age_max,
                "config": data["config"],
            }
            if item := existing_content.get(data["title"]):
                for field, value in values.items():
                    setattr(item, field, value)
            else:
                session.add(ContentItem(title=data["title"], **values))

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
