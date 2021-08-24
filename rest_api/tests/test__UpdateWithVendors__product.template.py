#!/usr/bin/python2

import requests, json


print '\n 1. Login in Odoo and get access tokens:'
r = requests.get(
    'http://localhost:8069/api/auth/get_tokens',
    headers = {'Content-Type': 'text/html; charset=utf-8'},
    data = json.dumps({
        # Tested only in Odoo v9 !!
        'username': 'admin',
        'password': 'admin',
    }),
    #verify = False      # for self-signed TLS/SSL certificates
)
print r.text
access_token = r.json()['access_token']


print '\n 2. product.template - Update one:'
r = requests.put(
    'http://localhost:8069/api/product.template/118',  # fill 'id' here!
    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'access_token': access_token
    },
    data = json.dumps({
        
        # simple field (non relational)
        'name': 'TEST Product (with vendors)~~',
        
        # one2many field (list of dictionaries of records)
        'seller_ids': [
            {   # this record will be updated (because 'id' is specified)
                
                'id':       49,  # ID of 'product.supplierinfo' record!
                
                'delay':    1,
                'min_qty':  10,
                'price':    80,
                'name':     55,  # 'res.partner' (Alpha Zone Limited)
            },
        ],
        
    }),
    #verify = False      # for self-signed TLS/SSL certificates
)
print r.text
