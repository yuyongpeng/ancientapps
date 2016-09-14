# coding: utf-8

import os
import re
import hashlib
import qrcode as qr
from json import loads
from datetime import datetime
from shutil import rmtree
from app import app, db, login_manager
from models import Beta, User
from ipa_parser import IpaFile
from flask import request, send_from_directory, render_template, jsonify, redirect, url_for, session, flash, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename

def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)


def fancy_password(username, password, salt):
    return hashlib.sha1('%s-%s-%s' % (username, password, salt)).hexdigest()


def check_admin():
    return g.user is not None and g.user.is_authenticated() and g.user.is_admin()


@app.before_request
def before_request():
    g.user = current_user
    g.host = app.config['HOST'][app.debug]


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/users/manager/')
def user_manager(page=1):
    if check_admin():
        users = User.query.paginate(page, 10, False)
        return render_template('user/manager.html', users=users, title=u'用户管理')
    else:
        abort(403)


@app.route('/users/<int:id>')
def user_info(id):
    if check_admin() or g.user.id == id:
        user = User.query.get(id)
        return render_template('user/detail.html', user=user, title=u'用户信息')
    else:
        abort(403)


@app.route('/users/level/<int:id>/<int:level>', methods=['POST'])
def user_level(id, level):
    if g.user is not None and g.user.is_authenticated():
        if g.user.is_admin():
            if level in range(3):
                user.level = level
            else:
                abort(400)
            user = User.query.get(id)
            db.session.add(user)
            db.session.commit()
        else:
            abort(403)
    else:
        flash(u'请先登录。', 'info')
        return redirect(url_for('login'))


@app.route('/users/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('user/register.html')
    salt = os.urandom(6).encode('hex')
    username = request.form['username']
    password = fancy_password(username, request.form['password'], salt)
    email = request.form['email']
    user = User(username=username, secret_password=password, email=email, salt=salt)
    db.session.add(user)
    db.session.commit()
    flash(u'注册成功', 'success')
    logout_user()
    return redirect(url_for('login'))


@app.route('/users/login',methods=['GET','POST'])
def login(next=None):
    if request.method == 'GET':
        if g.user is not None and g.user.is_authenticated():
            return redirect(url_for('index'))
        return render_template('user/login.html', title=u'登录') 
    else:
        username = request.form['username']
        password = request.form['password']
        remember_me = False
        if 'remember_me' in request.form:
            remember_me = True
        registered_user = User.query.filter_by(username=username).first()
        if registered_user == None:
            flash(u'用户名或密码无效。', 'danger')
            return redirect(url_for('login'))
        elif registered_user.secret_password != fancy_password(username, password, registered_user.salt):
            flash(u'用户名或密码无效。', 'danger')
            return redirect(url_for('login'))
        login_user(registered_user, remember = remember_me)
        flash(u'登录成功。', 'success')
        return redirect(redirect_url())


@app.route('/users/logout')
def logout():
    logout_user()
    flash(u'已注销。', 'info')
    return redirect(url_for('login'))


@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    if check_admin():
        betas = Beta.query\
                    .filter(Beta.is_deleted == False)\
                    .order_by(Beta.timestamp.desc())\
                    .paginate(page, 10, False)
        return render_template('app/index.html', betas=betas, page=page, title=u'首页')
    elif g.user is not None and g.user.is_authenticated():
        apps = loads(g.user.apps)
        betas = Beta.query\
                    .filter(Beta.is_deleted == False)\
                    .filter(Beta.bundle_id.in_(apps))\
                    .order_by(Beta.timestamp.desc())\
                    .paginate(page, 10, False)
        return render_template('app/index.html', betas=betas, page=page, title=u'首页')
    else:
        flash(u'请先登录。', 'info')
        return redirect(url_for('login'))


@app.route('/apps/manager/')
@app.route('/apps/manager/page/<int:page>')
def manager(page=1):
    if g.user is not None and g.user.is_authenticated():
        if g.user.is_admin():
            betas = Beta.query\
                        .order_by(Beta.timestamp.desc())\
                        .paginate(page, 10, False)
            return render_template('app/manager.html', betas=betas, title=u'应用管理')
        else:
            abort(403)
    else:
        flash(u'请先登录。', 'info')
        return redirect(url_for('login'))


@app.route('/apps/')
@app.route('/apps/page/<int:page>')
def search_app(page=1):
    if g.user is not None and g.user.is_authenticated():
        try:
            keyword = request.args.get('name')
            fkeyword = '%' + keyword + '%'
            betas = Beta.query\
                        .filter(Beta.is_deleted == False)\
                        .filter((Beta.name.like(fkeyword)) | (Beta.build.like(fkeyword)) | (Beta.version.like(fkeyword)))\
                        .order_by(Beta.timestamp.desc())\
                        .paginate(page, 10, False)
            return render_template('app/search.html', betas=betas, page=page, name=keyword, title=u'搜索 %s' % keyword)
        except:
            return redirect(url_for('index'))
    else:
        flash(u'请先登录。', 'info')
        return redirect(url_for('login'))


@app.route('/apps/show/<bundle_id>')
@app.route('/apps/show/<bundle_id>/<int:page>')
def show_app(bundle_id, page=1):
    betas = Beta.query\
                .filter(Beta.stable == True)\
                .filter(Beta.bundle_id == bundle_id)\
                .order_by(Beta.timestamp.desc())\
                .paginate(page, 10, False)
    try:
        title = betas.items[0].name
    except IndexError:
        title = u'应用列表'
    return render_template('app/show.html', page=page, betas=betas, bundle_id=bundle_id, title=title)


@app.route('/apps/show/builds/<int:id>')
def single_beta(id):
    beta = Beta.query.get(id)
    return render_template('app/detail.html', beta=beta, title=beta.name)


@app.route('/apps/<int:id>/publish')
def publish(id):
    if check_admin():
        candidate = Beta.query.get(id)
        candidate.stable = True
        db.session.add(candidate)
        db.session.commit()
        flash(u'发布成功', 'success')
        return redirect(redirect_url())
    else:
        abort(403)


@app.route('/apps/<int:id>/revoke')
def revoke(id):
    if check_admin():
        candidate = Beta.query.get(id)
        candidate.stable = False
        db.session.add(candidate)
        db.session.commit()
        flash(u'撤销成功', 'success')
        return redirect(redirect_url())
    else:
        abort(403)


@app.route('/apps/<int:id>/delete')
def delete(id):
    if check_admin():
        candidate = Beta.query.get(id)
        candidate.is_deleted = True
        db.session.add(candidate)
        db.session.commit()
        flash(u'删除成功', 'success')
        return redirect(redirect_url())
    else:
        abort(403)


@app.route('/apps/empty_trash')
def super_delete():
    if check_admin():
        deleted = []
        trash = Beta.query.filter(Beta.is_deleted == True)
        for t in trash:
            path = os.path.join(app.config['DOWNLOAD_DIR'], t.bundle_id, t.build)
            rmtree(path)
            deleted.append(t.id)
            db.session.delete(t)
            db.session.commit()
        return jsonify(deleted=deleted)
    else:
        abort(403)


@app.route('/stable/<team>')
@app.route('/stable/<team>/page/<int:page>')
def public_beta(team, page=1):
    if g.user is not None and g.user.is_authenticated():
        teams = dict(m3m=u'Modern Mobile Digital Media Company Limited',
                     ele=u'ELE Inc.')
        if team not in teams.keys():
            flash(u'你要找的东西不存在哟！', 'info')
            return redirect(url_for('index'))
        else:
            betas = Beta.query.filter(Beta.team == teams[team]).filter(Beta.stable == True).order_by(Beta.timestamp.desc()).paginate(page, 10, False)
            return render_template('app/stable.html', betas=betas, title='Apps', team=team, user=g.user)
    else:
        flash(u'请先登录。', 'info')
        return redirect(url_for('login', next=url_for('public_beta', team=team)))


@app.route('/upload', methods=['GET', 'POST'])
def old_upload():
    flash(u'请收藏上传页面的新地址：http://inhouse-test.bbwc.cn/apps/manager/upload', 'info')
    return redirect(url_for('upload'))


@app.route('/apps/manager/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        response = dict(apps=list())
        timestamp = datetime.strftime(datetime.now(), '%s')
        files = request.files.getlist('ipa[]')
        for f in files:
            print f
            filename = hashlib.md5(timestamp + secure_filename(f.filename)).hexdigest()
            with file(os.path.join(app.config['UPLOAD_DIR'], filename), 'w') as ipa:
                ipa.write(f.read())
            try:
                ipa = IpaFile(os.path.join(app.config['UPLOAD_DIR'], filename))
            except:
                response['code'] = '1'
                response['message'] = 'Bad IPA File.'
                return jsonify(response)
            result = ipa.save_ipa(app.config['DOWNLOAD_DIR'])
            if not ipa.save_icon(app.config['DOWNLOAD_DIR']):
                ipa.icon = ''
            link = ipa.gen_link(path=app.config['DOWNLOAD_DIR'],
                                template=app.config['PLIST_TEMPLATE'],
                                host=app.config['HOST'][app.debug])
            response['code'] = '0'
            response['message'] = 'Upload received.'
            response['timestamp'] = timestamp
            app_info = dict(name=ipa.display_name, icon=ipa.icon, team=ipa.team,
                            link=link, version=ipa.bundle_short_version,
                            build=ipa.build, bundle_id=ipa.bundle_id, qrcode=ipa.qrcode)
            beta = Beta(**app_info)
            db.session.add(beta)
            db.session.commit()
            app_info['id'] = beta.id
            qr_chunk = qr.make(g.host + url_for('single_beta', id=beta.id))
            qr_chunk.save(os.path.join(app.config['DOWNLOAD_DIR'], beta.qrcode))
            ipa.clean_up()
            response['apps'].append(app_info)
        return jsonify(response)
    else:
        return render_template('app/upload.html')


@app.route('/download/<bundle_id>/<bundle_version>/<filename>')
def get_file(bundle_id, bundle_version, filename):
    d = os.path.join(app.config['DOWNLOAD_DIR'], bundle_id, bundle_version)
    return send_from_directory(d, filename)


@app.route('/readme')
def readme():
    return render_template('misc/readme.html')
