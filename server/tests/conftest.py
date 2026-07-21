import os

# Unit tests must not import drivers or connect using a developer's local .env.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
