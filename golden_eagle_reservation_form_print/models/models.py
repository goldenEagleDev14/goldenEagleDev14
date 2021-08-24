# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    id_def_date = fields.Date('ID Date')
    work_place = fields.Char()