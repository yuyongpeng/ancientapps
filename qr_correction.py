#!flask/bin/python

from app import db, models
import os
import qrcode as qr

betas = models.Beta.query.all()
def repair_qr(beta):
	path = os.path.join(os.path.abspath(os.path.curdir), 'download')
	baseurl = 'https://inhouse-test.bbwc.cn/apps/show/builds'
	url = os.path.join(baseurl, str(beta.id))
	print url
	chunk = qr.make(url)
	print 'Saving QRCode for', beta.id, '...',
	try:
		chunk.save(os.path.join(path, beta.bundle_id, beta.build, 'qrcode.png'))
		print 'ok'
		beta.qrcode = os.path.join(beta.bundle_id, beta.build, 'qrcode.png')
		db.session.add(beta)
		db.session.commit()
	except:
		print 'fail!'

for beta in betas:
	repair_qr(beta)
