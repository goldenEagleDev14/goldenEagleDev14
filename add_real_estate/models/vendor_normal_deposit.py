# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime
from datetime import datetime, date,timedelta
from odoo.tools.translate import _
import calendar
from odoo.exceptions import ValidationError,UserError
import xlrd
import tempfile
import binascii
from operator import attrgetter
import logging
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

LOGGER = logging.getLogger(__name__)

class vendor_normal_deposit(models.Model):
    _name = 'vendor.normal.deposit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string="Date", required=True,default=fields.Date.today() )
    name = fields.Char(string="Number", required=False, )

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True, )
    delivery_date = fields.Date(string="Date", required=True )
    # withdrawal_date = fields.Date(string="Date", required=True )
    cheque_number = fields.Integer(copy=False,related="payment_ids.cheque_number")
    cheque_number_rel = fields.Char(related="payment_ids.cheque_number_rel",)
    payment_ids = fields.One2many('account.payment', 'vendor_normal_id', string="Payments", required=True,)
    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('delivery', 'Delivery') ], required=False ,default='draft')
    # create method
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('vendor.normal.deposit.seq')
        return super(vendor_normal_deposit, self).create(values)


    def multi_delivery(self):
        print("payment_ids :> ",self.payment_ids)
        for line in self.payment_ids:
            self.state = 'delivery'
            if line.state == 'posted':
                print("delivery_date :?> ",line.delivery_date)
                line.delivery_date = self.delivery_date
                print("delivery_date 22:?> ",line.delivery_date)
                line.with_context(delivery_aml=1).post()


    def multi_withdrawal(self):
        print("payment_ids :> ",self.payment_ids)
        for line in self.payment_ids:
            if line.state == 'deliver' and line.multi_select == True:
                print("delivery_date :?> ",line.withdrawal_date)
                line.withdrawal_date = line.ref_coll_vendor

                line.with_context(bank_aml=1).post()



    def multi_refund_delivery(self):
        print("payment_ids :> ",self.payment_ids)
        for line in self.payment_ids:
            if line.state == 'deliver' and line.multi_select == True:
                print("delivery_date :?> ",line.withdrawal_date)
                line.refund_delivery_date = line.ref_coll_vendor

                line.with_context(refund_delivery=1).refund_payable()


    def related_journal_button(self):
        return {
            'name': 'Journal Items',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.payment_ids.ids)],
            'context': {'group_by': ['payment_id']}
        }