# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DBCredential(models.Model):
    _name = 'db.credential'

    server_url = fields.Char('Server Url')
    db_name = fields.Char('DB Name')
    db_user = fields.Char('User')
    db_password = fields.Char('Password')
