# run these tests like:
#
#    python -m unittest test_user_model.py


from enum import unique
import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.m1_id = m1.id

        self.client = app.test_client()
    
    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        u1 = User.query.get(self.u1_id)
        m1 = u1.messages[0]

        # User should have one message
        self.assertEqual(len(u1.messages), 1)
        self.assertEqual(m1.text, "m1-text")
        self.assertEqual(self.u1_id, m1.user_id)