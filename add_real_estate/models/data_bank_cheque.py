# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
import datetime
from odoo.exceptions import ValidationError

class PaymentStrg(models.Model):
    _name = 'data.bank.cheque'
    _order = "id asc"

    name = fields.Char(string="", required=False,compute="_compute_name" )
    def _compute_name(self):
        for rec in self:
            if rec.payment_strg_id.state_payment == 'cheque':
                rec.name = rec.bank_id.name +"-"+ str(rec.cheque_number)
            else:
                rec.name = ''
    bank_id = fields.Many2one(comodel_name="payment.bank", string="Bank", required=False, )
    cheque_number = fields.Integer(string="Cheque Number",  required=False, )
    payment_strg_request_id = fields.Many2one(comodel_name="payment.strg.request", string="payment", required=False, )
    payment_strg_id = fields.Many2one(comodel_name="payment.strg", string="Payment", required=False, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="", required=False, )
    payment_id = fields.Many2one(comodel_name="account.payment", string="", required=False, )