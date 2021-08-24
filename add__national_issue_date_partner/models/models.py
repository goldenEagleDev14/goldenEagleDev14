# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    national_issue_date = fields.Date(string="National issue date", required=False, )