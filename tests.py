#!/usr/bin/env python
import os
import unittest
from datetime import datetime, timedelta

# Coverage
from coverage import coverage
cov = coverage(branch = True, omit = ['flask/*', 'tests.py'])
cov.start()


from config import basedir
from app import app, db
from app.models import User, Post

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_avatar(self):
		u = User(nickname = 'john', email = 'john@example.com')
		avatar = u.avatar(128)
		expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
		assert avatar[0:len(expected)] == expected

	def test_make_unique_nickname(self):
		# create a user and write it to the database
		u = User(nickname = 'john', email = 'john@example.com')
		db.session.add(u)
		db.session.commit()
		nickname = User.make_unique_nickname('susan')
		assert nickname == 'susan'
		nickname = User.make_unique_nickname('john')
		assert nickname != 'john'
		u = User(nickname = nickname, email = 'susan@example.com')
		db.session.add(u)
		db.session.commit()
		nickname2 = User.make_unique_nickname('john')
		assert nickname2 != 'john'
		assert nickname2 != nickname

	def test_follow(self):
		u1 = User(nickname = 'john', email = 'john@example.com')
		u2 = User(nickname = 'susan', email = 'susan@example.com')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		assert u1.unfollow(u2) == None
		u = u1.follow(u2)
		db.session.add(u)
		db.session.commit()
		assert u1.follow(u2) == None
		assert u1.is_following(u2)
		assert u1.followed.count() == 1
		assert u1.followed.first().nickname == 'susan'
		assert u2.followers.count() == 1
		assert u2.followers.first().nickname == 'john'
		u = u1.unfollow(u2)
		assert u != None
		db.session.add(u)
		db.session.commit()
		assert u1.is_following(u2) == False
		assert u1.followed.count() == 0
		assert u2.followers.count() == 0

	def test_follow_posts(self):
		# make four users
		u1 = User(nickname = 'john', email = 'john@example.com')
		u2 = User(nickname = 'susan', email = 'susan@example.com')
		u3 = User(nickname = 'mary', email = 'mary@example.com')
		u4 = User(nickname = 'david', email = 'david@example.com')
		db.session.add(u1)
		db.session.add(u2)
		db.session.add(u3)
		db.session.add(u4)
		# make four posts
		utcnow = datetime.utcnow()
		p1 = Post(body = "post from john", author = u1, timestamp = utcnow + timedelta(seconds = 1))
		p2 = Post(body = "post from susan", author = u2, timestamp = utcnow + timedelta(seconds = 2))
		p3 = Post(body = "post from mary", author = u3, timestamp = utcnow + timedelta(seconds = 3))
		p4 = Post(body = "post from david", author = u4, timestamp = utcnow + timedelta(seconds = 4))
		db.session.add(p1)
		db.session.add(p2)
		db.session.add(p3)
		db.session.add(p4)
		db.session.commit()
		# setup the followers
		u1.follow(u1) # john follows himself
		u1.follow(u2) # john follows susan
		u1.follow(u4) # john follows david
		u2.follow(u2) # susan follows herself
		u2.follow(u3) # susan follows mary
		u3.follow(u3) # mary follows herself
		u3.follow(u4) # mary follows david
		u4.follow(u4) # david follows himself
		db.session.add(u1)
		db.session.add(u2)
		db.session.add(u3)
		db.session.add(u4)
		db.session.commit()
		# check the followed posts of each user
		f1 = u1.followed_posts().all()
		f2 = u2.followed_posts().all()
		f3 = u3.followed_posts().all()
		f4 = u4.followed_posts().all()
		assert len(f1) == 3
		assert len(f2) == 2
		assert len(f3) == 2
		assert len(f4) == 1
		assert f1 == [p4, p2, p1]
		assert f2 == [p3, p2]
		assert f3 == [p4, p3]
		assert f4 == [p4]

	def test_delete_post(self):
		# create a user and a post
		u = User(nickname='john', email='john@example.com')
		p = Post(body = 'test post', author = u, timestamp = datetime.utcnow())
		db.session.add(u)
		db.session.add(p)
		db.session.commit()
		# query the post and destroy the session
		p = Post.query.get(1)
		db.session.remove()
		# delete the post using a new session
		db.session = db.create_scoped_session()
		db.session.delete(p)
		db.session.commit()

	def test_user(self):
		# make valid nicknames
		n = User.make_valid_nickname('John_123')
		assert n == 'John_123'
		n = User.make_valid_nickname('John_[123]\n')
		assert n == 'John_123'
		# create a user
		u = User(nickname = 'john', email = 'john@example.com')
		db.session.add(u)
		db.session.commit()
		assert u.is_authenticated() == True
		assert u.is_active() == True
		assert u.is_anonymous() == False
		assert u.id == int(u.get_id())

if __name__ == '__main__':
	try:
		unittest.main()
	except:
		pass
	cov.stop()
	cov.save()
	print "\n\nCoverage Report:\n"
	cov.report()
	print "HTML version: " + os.path.join(basedir, "tmp/coverage/index.html")
	cov.html_report(directory = 'tmp/coverage')
	cov.erase()