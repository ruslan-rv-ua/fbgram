from enum import Enum
from typing import Self

from piccolo.columns import JSON, Text, Timestamp, Varchar
from piccolo.table import Table

from .db import database


class PostStatus(str, Enum):
    NEW = "new"
    SENT = "sent"
    FAILED = "failed"


class Post(Table, db=database, tablename="posts"):
    id = Varchar(primary_key=True, length=24)
    created_at = Timestamp()
    short_html = Text()
    metadata = JSON()
    status = Varchar(default=PostStatus.NEW, length=16, choices=PostStatus)


class Settings(Table, db=database, tablename="settings"):  #! TODO: make it singleton
    id = Varchar(primary_key=True, length=24)

    telegram_bot_token = Varchar(length=64, null=True, default=None)
    telegram_chat_id = Varchar(length=64, null=True, default=None)

    facebook_email = Varchar(length=64, null=True, default=None)
    facebook_password = Varchar(length=64, null=True, default=None)

    @classmethod
    def load(cls) -> Self:
        settings = cls.objects().first().run_sync()
        if settings is None:
            settings = cls()
            settings.save()
        return settings

    def save(self):
        super().save().run_sync()
        self.refresh().run_sync()


# Create tables if they don't exist
Post.create_table(if_not_exists=True).run_sync()
Settings.create_table(if_not_exists=True).run_sync()
