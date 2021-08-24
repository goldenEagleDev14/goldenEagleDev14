from odoo import api, fields, models


class CheckType(models.Model):
    _name = 'check.type'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char()
