from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
migration_tmp = Table('migration_tmp', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String),
    Column('password', String),
    Column('nickname', String),
    Column('email', String),
    Column('group', String),
    Column('apps', String),
    Column('is_admin', Boolean),
    Column('registered_on', DateTime),
)

users = Table('users', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=50)),
    Column('secret_password', String(length=40)),
    Column('salt', String(length=12)),
    Column('nickname', String(length=10)),
    Column('email', String(length=50)),
    Column('group', String(length=50)),
    Column('apps', String(length=240)),
    Column('level', Integer),
    Column('registered_on', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['migration_tmp'].drop()
    post_meta.tables['users'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['migration_tmp'].create()
    post_meta.tables['users'].drop()
