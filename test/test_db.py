from fbgram.db.db import database
from fbgram.db.models import Post, Settings


def test_create_db_file():
    assert database.path
