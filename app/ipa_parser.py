# coding: utf-8

import re
import os
import shutil
from app import ipin
from zipfile import ZipFile
from biplist import readPlist

_TMP = '/tmp'

class IpaFile(ZipFile):

    @property
    def info(self):
        for f in self.namelist():
            if os.path.basename(f) == "Info.plist":
                if len(f.split('/')) == 3:
                    d = readPlist(self.extract(f, path=_TMP))
                    return d
        return None

    @property
    def base_dir(self):
        return self.namelist()[1]

    @property
    def display_name(self):
        return self.info['CFBundleDisplayName']

    @property
    def bundle_id(self):
        return self.info['CFBundleIdentifier']

    @property
    def bundle_short_version(self):
        return self.info['CFBundleShortVersionString']

    @property
    def team(self):
        try:
            p = os.path.join(self.namelist()[1], "embedded.mobileprovision")
            with file(self.extract(p, path=_TMP), 'rb') as f:
                patt = re.compile(r'TeamName</key>\n.*')
                team = patt.findall(f.read())[0]\
                           .strip('</string>')\
                           .lstrip('TeamName</key>\n\t<string>')\
                           .lstrip('<string>')
            return team
        except KeyError:
            return 'N/A'

    def create_dir(self, path, suffix=None):
        print path
        try:
            os.mkdir(os.path.join(path, self.bundle_id))
        except OSError, e:
            print e
            pass
        try:
            if suffix:
                os.mkdir(os.path.join(path, self.bundle_id, self.info['CFBundleVersion'] + "-%d" % suffix))
            else:
                os.mkdir(os.path.join(path, self.bundle_id, self.info['CFBundleVersion']))
        except OSError, e:
            print e
            pass


    def save_ipa(self, path, suffix=0):
        self.build = self.info['CFBundleVersion']
        if suffix:
            self.build += "-%d" % suffix
        target = os.path.join(self.bundle_id, self.build)
        if os.path.isdir(os.path.join(path, target)):
            suffix += 1
            return self.save_ipa(path=path, suffix=suffix)
        self.create_dir(path, suffix=suffix)
        shutil.copy(self.filename, os.path.join(path, target, 'app.ipa'))
        self.ipa_file = os.path.join(target, 'app.ipa')
        return self.ipa_file


    def save_icon(self, path):
        self.icon = os.path.join(self.bundle_id, self.build, 'icon.png')
        try:
            source, largest = (None, None)
            for icon in [ x for x in self.namelist() if x.split('/')[-1].startswith('AppIcon') and x.endswith('.png') ]:
                size = self.getinfo(icon).file_size
                source, largest = [(source, largest), (icon, size)][size > largest]
        except:
            self.icon = "http://inhouse-test.bbwc.cn/static/icon-256.png"
            return self.icon
        self.create_dir(path)
        try:
            shutil.move(self.extract(source, path=_TMP), os.path.join(path, self.icon))
            ipin.updatePNG(os.path.join(path,self.icon))
        except:
            self.icon = "../static/icon-256.png"
        return self.icon


    def gen_link(self, path, template, host):
        link_template = 'itms-services://?action=download-manifest&url=%s'
        plist = os.path.join(path, self.bundle_id, self.build, 'manifest.plist')
        plist_url = plist.replace(path, host + '/download')
        info = {'ipa_file': '/'.join([host, 'download', self.ipa_file]),
                'icon': '/'.join([host, 'download', self.icon]),
                'bundle_id':self.bundle_id,
                'version':self.build,
                'display_name':self.display_name.encode('utf-8') }
        t = file(template).read()
        with file(plist, 'w') as p:
            p.write(t % info)
        self.link = link_template % plist_url
        self.qrcode = os.path.join(self.bundle_id, self.build, 'qrcode.png')
        self.create_dir(path)
        return self.link


    def clean_up(self):
        return os.remove(self.filename)
