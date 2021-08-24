# -*- coding: utf-8 -*-

import xmlrpc.client
info = xmlrpc.client.ServerProxy('https://demo.odoo.com/start').start()
url, db, username, password = \
    info['host'], info['database'], info['user'], info['password']

print("info :>",info)
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
models.execute_kw(db, uid, password,
    'res.partner', 'check_access_rights',
    ['read'], {'raise_exception': False})

