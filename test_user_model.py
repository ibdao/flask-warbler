"""User model tests."""

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


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_repr(self):
        """Checks the dunder repr is accurate"""
        u1 = User.query.get(self.u1_id)
        self.assertEqual(repr(u1),f"<User #{u1.id}: {u1.username}, {u1.email}>")

    def test_is_following(self):
        """Tests for following another user and followed by another user"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        u1.following.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))

        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u1.is_followed_by(u2))

    def test_user_sign_up(self):
        """Tests for signing up a user with valid credentials
        Expect an IntegrityError when trying to sign up with duplicated credentials """
       
        u3 = User.signup("u3", "u3@email.com", "password", None)

        db.session.commit()
        self.u3_id = u3.id


        def duplicate_user():
            """Creates a duplicate user and updates the database"""

            User.signup("u3", "u3@email.com", "password", None)
            db.session.commit()
        
        users = User.query.all()
        self.assertIn(u3, users)
        self.assertRaises(exc.IntegrityError, duplicate_user)
    
    def test_user_authenticate(self):
        u1 = User.query.get(self.u1_id)
        
        self.assertTrue(User.authenticate(u1.username, "password"))
        self.assertFalse(User.authenticate("u4", "password"))
        self.assertFalse(User.authenticate(u1.username, "drowssap"))
