# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    broker_commission_amount = fields.Float(_('Broker Commission Percentage'))
    broker_commission_account = fields.Many2one('account.account', _('Broker Commission Account'))
    organization = fields.Char(_('Organization'))
    partner_code = fields.Char(string="Partner Code", readonly=True, copy=False)
    mobile1_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], string="Mobile1 Type")
    mobile2 = fields.Char('Mobile 2')
    mobile2_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], string="Mobile2 Type")

