# coding: utf-8
import os, sys, site
sys.path.insert(0, os.path.split(os.path.abspath(__file__))[0])
_basedir = os.path.split(os.path.abspath(__file__))[0]
activate_this = os.path.join(_basedir, 'flask/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
site.addsitedir(os.path.abspath(__file__))
from app import app as application

