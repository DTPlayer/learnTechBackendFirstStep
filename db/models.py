from tortoise import Model, fields
import uuid

class User(Model):
    id = fields.BigIntField(pk=True)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255)
    middle_name = fields.CharField(max_length=255)
    login = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)


class Token(Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="tokens")
    token = fields.TextField()
    expires_at = fields.BigIntField()


class Board(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)


class Card(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    board = fields.ForeignKeyField("models.Board", related_name="cards")
    first_name_candidate = fields.CharField(max_length=255)
    last_name_candidate = fields.CharField(max_length=255)
    middle_name_candidate = fields.CharField(max_length=255)
    hr = fields.ForeignKeyField("models.User", related_name="cards")
    date_of_birth_candidate = fields.DatetimeField()
    job_title = fields.CharField(max_length=255)
    salary = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    status = fields.CharField(max_length=255)


class CardFiles(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    card = fields.ForeignKeyField("models.Card", related_name="fields")
    file_path = fields.CharField(max_length=255)
    file_metadata = fields.JSONField()

__all__ = (
    "User",
    "Token",
    "Board",
    "Card",
    "CardFiles"
)
