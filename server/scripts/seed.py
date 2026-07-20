"""Seed the local database with a minimal development record."""

from sqlalchemy import create_engine, text

from app.config import get_settings


def seed() -> None:
    engine = create_engine(get_settings().database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS baby_profiles (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    birth_date DATE NOT NULL
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO baby_profiles (id, name, birth_date)
                VALUES ('demo-baby', 'Demo Baby', '2026-01-01')
                ON CONFLICT (id) DO NOTHING
                """
            )
        )
    print("Seed data is ready.")


if __name__ == "__main__":
    seed()
