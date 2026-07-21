"""Reset and seed a deterministic, presentation-ready Swaddle demo database."""

from calendar import monthrange
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import delete, text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    Baby,
    ConsultationSlot,
    ContentItem,
    ContentType,
    Prescription,
    PrescriptionStatus,
    Product,
    SlotStatus,
    SymptomQuery,
    User,
    UserRole,
)
from app.prescriptions.constants import AI_DISCLAIMER

COMMONS_MEDIA = "https://commons.wikimedia.org/wiki/Special:Redirect/file/"

PRODUCTS = [
    # Pharmacy and OTC care supplies. Product names deliberately avoid dosage advice.
    (
        "Sterile Saline Nasal Drops",
        "pharmacy",
        0,
        24,
        "6.49",
        ["nasal", "congestion", "otc"],
    ),
    (
        "Zinc Oxide Diaper Rash Cream",
        "pharmacy",
        0,
        36,
        "8.99",
        ["diaper-rash", "skin", "otc"],
    ),
    (
        "Flexible-Tip Digital Thermometer",
        "pharmacy",
        0,
        36,
        "14.99",
        ["fever", "temperature", "safety"],
    ),
    (
        "Benzocaine-Free Cooling Teething Gel",
        "pharmacy",
        6,
        24,
        "7.79",
        ["teething", "gums", "otc"],
    ),
    (
        "Infant Fever Reducer — Clinician-Guided Use",
        "pharmacy",
        2,
        24,
        "9.49",
        ["fever", "clinician-guidance", "otc"],
    ),
    # Toys selected to make the three demo ages visibly different.
    ("Soft Wrist Rattle Pair", "toy", 0, 5, "12.99", ["rattle", "hearing", "grasp"]),
    (
        "High-Contrast Crinkle Cards",
        "toy",
        0,
        6,
        "10.50",
        ["visual", "tummy-time", "sensory"],
    ),
    (
        "Rainbow Stacking Rings",
        "toy",
        6,
        15,
        "18.99",
        ["stacking", "motor-skills", "colors"],
    ),
    ("Textured Sensory Balls", "toy", 6, 18, "16.49", ["sensory", "grasp", "rolling"]),
    (
        "Wooden Shape Sorter",
        "toy",
        12,
        30,
        "27.99",
        ["shapes", "problem-solving", "motor-skills"],
    ),
    # General everyday supplies.
    (
        "Newborn Sensitive Diapers — 40 Pack",
        "supplies",
        0,
        4,
        "19.99",
        ["diapering", "hypoallergenic"],
    ),
    (
        "Fragrance-Free Baby Wipes — 72 Pack",
        "supplies",
        0,
        36,
        "5.99",
        ["diapering", "sensitive-skin"],
    ),
    (
        "Wi-Fi Baby Monitor with Night Vision",
        "supplies",
        0,
        36,
        "79.99",
        ["sleep", "monitor", "safety"],
    ),
    (
        "Anti-Colic Bottle Set",
        "supplies",
        0,
        12,
        "24.99",
        ["feeding", "bottle", "anti-colic"],
    ),
    (
        "Waterproof Toddler Bib Set",
        "supplies",
        6,
        30,
        "13.99",
        ["feeding", "washable", "weaning"],
    ),
]

CONTENT_ITEMS = [
    # Free/public-domain recordings with their source and license kept auditable.
    (
        "rhyme",
        "Twinkle, Twinkle, Little Star",
        f"{COMMONS_MEDIA}Twinkle_Twinkle_Little_Star_plain.ogg",
        0,
        24,
        {
            "provider": "Wikimedia Commons",
            "license": "Public domain",
            "source_page": "https://commons.wikimedia.org/wiki/File:Twinkle_Twinkle_Little_Star_plain.ogg",
        },
    ),
    (
        "rhyme",
        "Itsy Bitsy Spider",
        f"{COMMONS_MEDIA}Itsy_Bitsy_Spider.ogg",
        3,
        24,
        {
            "provider": "Wikimedia Commons",
            "license": "CC BY-SA 3.0 / GFDL",
            "source_page": "https://commons.wikimedia.org/wiki/File:Itsy_Bitsy_Spider.ogg",
        },
    ),
    (
        "rhyme",
        "Row, Row, Row Your Boat",
        f"{COMMONS_MEDIA}Row%2C_Row%2C_Row_Your_Boat.ogg",
        3,
        24,
        {
            "provider": "Wikimedia Commons",
            "license": "CC BY-SA 3.0 / GFDL",
            "source_page": "https://commons.wikimedia.org/wiki/File:Row,_Row,_Row_Your_Boat.ogg",
        },
    ),
    (
        "rhyme",
        "Mary Had a Little Lamb",
        f"{COMMONS_MEDIA}Mary_Had_a_Little_Lamb.ogg",
        6,
        24,
        {
            "provider": "Wikimedia Commons",
            "license": "Public domain",
            "source_page": "https://commons.wikimedia.org/wiki/File:Mary_Had_a_Little_Lamb.ogg",
        },
    ),
    (
        "rhyme",
        "Baa, Baa, Black Sheep",
        f"{COMMONS_MEDIA}Bahbahblacksheep.ogg",
        6,
        24,
        {
            "provider": "Wikimedia Commons",
            "license": "CC0 1.0",
            "source_page": "https://commons.wikimedia.org/wiki/File:Bahbahblacksheep.ogg",
        },
    ),
    # URL is the embeddable YouTube video ID, not a full watch URL.
    (
        "video",
        "Animal Sounds Song",
        "33UG1Uch05Y",
        6,
        24,
        {"provider": "youtube", "channel": "Kids TV", "topic": "animals and listening"},
    ),
    (
        "video",
        "First Alphabet Song",
        "cE3LzPQgQmk",
        12,
        24,
        {"provider": "youtube", "channel": "Kids TV", "topic": "early language"},
    ),
    (
        "video",
        "Wash Your Hands",
        "kToNHhH74yo",
        12,
        24,
        {"provider": "youtube", "channel": "Kids TV", "topic": "healthy routines"},
    ),
    (
        "video",
        "Learn Vehicles for Babies",
        "OIHKD8ACzzY",
        12,
        24,
        {
            "provider": "youtube",
            "channel": "CoComelon — Nina's Familia",
            "topic": "vehicles and environments",
        },
    ),
    (
        "video",
        "This Is the Way",
        "O6uap1FZmzc",
        18,
        24,
        {
            "provider": "youtube",
            "channel": "Scoopy Cap",
            "topic": "daily routines and language",
        },
    ),
    # Generated Web Audio cues: no copyrighted asset or hardcoded game UI required.
    (
        "sound",
        "Where Did the Soft Bell Go?",
        "generated://hearing/soft-bell",
        0,
        6,
        {
            "description": (
                "Play a gentle bell cue on alternating sides and pause for the "
                "baby to orient."
            ),
            "generator": "oscillator",
            "waveform": "sine",
            "frequency_hz": 523.25,
            "duration_ms": 500,
            "gain": 0.10,
        },
    ),
    (
        "sound",
        "Low and High Tone Turn-Taking",
        "generated://hearing/low-high",
        6,
        15,
        {
            "description": (
                "Alternate two short tones and encourage a reach after each cue."
            ),
            "cues": [
                {"label": "low", "frequency_hz": 261.63},
                {"label": "high", "frequency_hz": 523.25},
            ],
            "duration_ms": 450,
            "gain": 0.12,
        },
    ),
    (
        "sound",
        "Copy the Three-Sound Pattern",
        "generated://hearing/pattern",
        15,
        24,
        {
            "description": (
                "Play a three-tone pattern and invite the toddler to tap the "
                "sequence back."
            ),
            "cues": [329.63, 392.00, 329.63],
            "duration_ms": 350,
            "gain": 0.12,
        },
    ),
    (
        "activity",
        "Primary Color Match",
        "game://color-theory/primary",
        8,
        20,
        {
            "game_type": "color_pair_match",
            "instructions": "Match two cards with the same primary color.",
            "colors": [
                {"id": "red", "label": "Red", "hex": "#EF4444"},
                {"id": "yellow", "label": "Yellow", "hex": "#FACC15"},
                {"id": "blue", "label": "Blue", "hex": "#3B82F6"},
            ],
            "matching_pairs": [["red", "red"], ["yellow", "yellow"], ["blue", "blue"]],
            "shuffle": True,
        },
    ),
    (
        "activity",
        "Warm and Cool Color Match",
        "game://color-theory/warm-cool",
        15,
        24,
        {
            "game_type": "color_group_match",
            "instructions": "Match each color card to its warm or cool basket.",
            "colors": [
                {"id": "orange", "label": "Orange", "hex": "#F97316", "group": "warm"},
                {"id": "pink", "label": "Pink", "hex": "#EC4899", "group": "warm"},
                {"id": "green", "label": "Green", "hex": "#22C55E", "group": "cool"},
                {"id": "purple", "label": "Purple", "hex": "#9333EA", "group": "cool"},
            ],
            "matching_pairs": [
                ["orange", "warm"],
                ["pink", "warm"],
                ["green", "cool"],
                ["purple", "cool"],
            ],
            "shuffle": True,
        },
    ),
]


def months_ago(months: int, today: date) -> date:
    """Return the same day-of-month N months ago, clamped for short months."""
    absolute_month = today.year * 12 + today.month - 1 - months
    year, zero_based_month = divmod(absolute_month, 12)
    month = zero_based_month + 1
    return date(year, month, min(today.day, monthrange(year, month)[1]))


def clear_demo_data(session: Session) -> None:
    """Clear all application rows and reset IDs for repeatable demo URLs."""
    if session.bind is not None and session.bind.dialect.name == "postgresql":
        session.execute(
            text(
                "TRUNCATE TABLE consultation_slots, content_items, products, "
                "prescriptions, symptom_queries, babies, users "
                "RESTART IDENTITY CASCADE"
            )
        )
        return

    for model in (
        Prescription,
        SymptomQuery,
        Baby,
        ConsultationSlot,
        ContentItem,
        Product,
        User,
    ):
        session.execute(delete(model))


def seed() -> None:
    today = date.today()
    with SessionLocal.begin() as session:
        clear_demo_data(session)

        parent = User(
            email="parent@swaddle.demo",
            role=UserRole.PARENT,
            hashed_password="$2b$12$demoParentHashNotForProduction",
        )
        reviewer = User(
            email="reviewer@swaddle.demo",
            role=UserRole.REVIEWER,
            hashed_password="$2b$12$demoReviewerHashNotForProduction",
        )
        session.add_all([parent, reviewer])
        session.flush()

        babies = [
            Baby(user_id=parent.id, name="Aarav", dob=months_ago(2, today), sex="male"),
            Baby(
                user_id=parent.id, name="Maya", dob=months_ago(8, today), sex="female"
            ),
            Baby(user_id=parent.id, name="Noah", dob=months_ago(18, today), sex="male"),
        ]
        session.add_all(babies)
        session.flush()

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
        )
        session.add_all(
            ContentItem(
                type=ContentType(kind),
                title=title,
                url=url,
                age_min_months=age_min,
                age_max_months=age_max,
                config=config,
            )
            for kind, title, url, age_min, age_max, config in CONTENT_ITEMS
        )

        session.add_all(
            [
                Prescription(
                    baby_id=babies[0].id,
                    file_url="demo-upload:///aarav-saline-note.png",
                    extracted_text={
                        "medicine_names": ["Saline nasal drops"],
                        "dosage_text": ["2 drops"],
                        "frequency_text": ["when needed"],
                        "raw_ocr_text": "Saline nasal drops - 2 drops when needed",
                        "ai_disclaimer": AI_DISCLAIMER,
                    },
                    status=PrescriptionStatus.PENDING_REVIEW,
                ),
                Prescription(
                    baby_id=babies[1].id,
                    file_url="demo-upload:///maya-clinic-prescription.pdf",
                    extracted_text={
                        "medicine_names": ["Vitamin D3 drops"],
                        "dosage_text": ["400 IU"],
                        "frequency_text": ["once daily"],
                        "raw_ocr_text": "Vitamin D3 drops 400 IU once daily",
                        "ai_disclaimer": AI_DISCLAIMER,
                    },
                    status=PrescriptionStatus.REVIEWED,
                    reviewer_id=reviewer.id,
                    reviewer_note=(
                        "Text matches the uploaded prescription; parent advised to "
                        "follow the clinician's directions."
                    ),
                ),
                Prescription(
                    baby_id=babies[2].id,
                    file_url="demo-upload:///noah-handwritten-prescription.jpg",
                    extracted_text={
                        "medicine_names": ["Amoxicillin"],
                        "dosage_text": ["?25 mg / 5 mL"],
                        "frequency_text": ["twice daily?"],
                        "raw_ocr_text": "Amoxicillin ?25 mg/5mL twice daily?",
                        "ai_disclaimer": AI_DISCLAIMER,
                    },
                    status=PrescriptionStatus.FLAGGED,
                    reviewer_id=reviewer.id,
                    reviewer_note=(
                        "Strength and frequency are unclear. Confirm with the "
                        "prescribing clinician or pharmacist before use."
                    ),
                ),
            ]
        )

        low_response = {
            "possible_causes": [
                "A mild viral upper-respiratory illness",
                "Dry air or environmental irritation",
            ],
            "home_care": [
                "Offer regular feeds and fluids",
                "Use a cool-mist humidifier and monitor symptoms",
            ],
            "red_flags": [
                "Breathing becomes difficult",
                "Feeding drops significantly or wet diapers decrease",
            ],
            "alert_level": "low",
            "disclaimer": "This is not medical advice.",
        }
        high_response = {
            "possible_causes": ["An infection requiring urgent in-person assessment"],
            "home_care": [
                "Keep the baby comfortably dressed while arranging urgent care"
            ],
            "red_flags": ["Fever in a baby younger than 3 months"],
            "alert_level": "high",
            "disclaimer": "This is not medical advice.",
        }
        session.add_all(
            [
                SymptomQuery(
                    baby_id=babies[1].id,
                    symptoms="Mild runny nose, playful and feeding normally",
                    age_months=8,
                    ai_response=low_response,
                    alert_level="low",
                    created_at=datetime.now(UTC) - timedelta(hours=18),
                ),
                SymptomQuery(
                    baby_id=babies[0].id,
                    symptoms="Fever in a two-month-old baby",
                    age_months=2,
                    ai_response=high_response,
                    alert_level="high",
                    created_at=datetime.now(UTC) - timedelta(hours=3),
                ),
            ]
        )

        clinicians = [
            "Dr. Asha Menon — Neonatology",
            "Dr. Rahul Iyer — General Pediatrics",
            "Dr. Meera Shah — Pediatric Nutrition",
            "Dr. Nikhil Rao — Pediatric Allergy",
            "Dr. Kavya Patel — Developmental Pediatrics",
        ]
        slot_times = [
            (1, 9, 0),
            (1, 10, 30),
            (1, 14, 0),
            (1, 16, 30),
            (2, 9, 30),
            (2, 11, 0),
            (2, 15, 0),
            (3, 9, 0),
            (3, 13, 30),
            (3, 17, 0),
        ]
        session.add_all(
            ConsultationSlot(
                pediatrician_name=clinicians[index % len(clinicians)],
                slot_time=datetime.combine(
                    today + timedelta(days=day), time(hour, minute), tzinfo=UTC
                ),
                status=(
                    SlotStatus.BOOKED if index in {1, 4, 8} else SlotStatus.AVAILABLE
                ),
            )
            for index, (day, hour, minute) in enumerate(slot_times)
        )

    print("Reset complete: 2 users, 3 babies, 15 products, 15 content items,")
    print("3 prescriptions, 2 symptom queries, and 10 consultation slots seeded.")
    print("Demo baby IDs: 1 = 2 months, 2 = 8 months, 3 = 18 months.")


if __name__ == "__main__":
    seed()
