#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.script import Manager, Command, Option
from app import app, db

import os
import imp
from migrate.versioning import api

from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO

# Translation Management Commands
class InitTranslation(Command):
	"Initializes a new language translation catalogue."

	option_list = (
		Option('--language', '-l', dest='languagecode'),
	)

	def run(self, languagecode):
		# Example: ./manager trinit -l fr
		if languagecode != None:
			os.system('pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app')
			os.system('pybabel init -i messages.pot -d app/translations -l %s' % languagecode)
			os.unlink('messages.pot')
		else:
			print 'You must provide a valid language code.'
			print 'Example command to start a French translation: python manager trinit -l fr'

class UpdateTranslations(Command):
	"Updates the translations with pybabel extract and update commands."

	def run(self):
		# Example: ./manager trupdate
		os.system('pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app')
		os.system('pybabel update -i messages.pot -d app/translations')
		os.unlink('messages.pot')
		print 'Translations updated.'

class CompileTranslations(Command):
	"Compiles the translations with the pybabel compile command."

	def run(self):
		# Example: ./manager trcompile
		os.system('pybabel compile -d app/translations')

# Database Management Commands
class CreateDatabase(Command):
	"Creates a SQLAlchemy database and migration repo for it."

	def run(self):
		db.create_all()
		if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
			api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
			api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
		else:
			api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

class MigrateDatabase(Command):
	"Migrates the database - updates database with current models."

	def run(self):
		migration = SQLALCHEMY_MIGRATE_REPO + '/versions/%03d_migration.py' % (api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO) + 1)
		tmp_module = imp.new_module('old_model')
		old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
		exec old_model in tmp_module.__dict__
		script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
		open(migration, "wt").write(script)
		api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
		print 'New migration saved as', migration
		print 'Current database version:', str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))

class UpgradeDatabase(Command):
	"Upgrades a database i.e. brings a database up to most recent migration version."

	def run(self):
		api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
		print 'Current database version:', str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))

class DowngradeDatabase(Command):
	"Downgrades a database i.e. rollback in migration versioning."

	def run(self):
		v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
		api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
		print 'Current database version:', str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))

manager = Manager(app)
manager.add_command('trinit', InitTranslation())
manager.add_command('trupdate', UpdateTranslations())
manager.add_command('trcompile', CompileTranslations())

manager.add_command('dbcreate', CreateDatabase())
manager.add_command('dbmigrate', MigrateDatabase())
manager.add_command('dbupgrade', UpgradeDatabase())
manager.add_command('dbdowngrade', DowngradeDatabase())

if __name__ == "__main__":
    manager.run()