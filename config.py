# coding: utf-8
import os

SECRET_KEY = '3405df885953dfd577f7ffdd1e80c49e5166e9b8'

_basedir = os.path.abspath(os.path.dirname(__file__))

TEMP_DIR = os.path.join(_basedir, 'tmp')
UPLOAD_DIR = os.path.join(_basedir, 'upload')
DOWNLOAD_DIR = os.path.join(_basedir, 'download')
PLIST_TEMPLATE = os.path.join(_basedir, 'plist.template')
HOST = ['https://inhouse-test.bbwc.cn', 'https://inhouse-test.bbwc.cn', 'http://127.0.0.1:5000']

TEAM = {'mm': 'Modern Mobile Digital Media Company Limited', 'ele': 'ELE Inc.'}

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(_basedir, 'db_repository')

print SQLALCHEMY_DATABASE_URI
print SQLALCHEMY_MIGRATE_REPO

