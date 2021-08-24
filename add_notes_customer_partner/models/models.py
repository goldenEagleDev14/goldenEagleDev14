# -*- coding: utf-8 -*-

from odoo import models, fields, api

class customerPayment(models.Model):
    _inherit = 'customer.payment'

    note = fields.Text(string="Note", required=False, )



class loanLineRsWizard(models.Model):
    _inherit = 'loan.line.rs.wizard'

    note = fields.Text(string="Note", required=False, )