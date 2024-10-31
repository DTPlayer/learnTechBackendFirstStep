from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "cardfields" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "file_path" VARCHAR(255) NOT NULL,
    "file_metadata" JSON NOT NULL,
    "card_id" CHAR(36) NOT NULL REFERENCES "card" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "cardfields";"""
