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

TYPE_SELECTION = [('sale', _('Sale')),
                  ('sale_refund', _('Sale Refund')),
                  ('purchase', _('Purchase')),
                  ('purchase_refund', _('Purchase Refund')),
                  ('cash', _('Cash')),
                  ('bank', _('Bank and Checks')),
                  ('general', _('General')),
                  ('situation', _('Opening/Closing Situation'))]
LOGGER = logging.getLogger(__name__)

class Customer_payment(models.Model):
    _name = 'customer.payment'
    _description = "Property Reservation"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date(string="Date", required=True,default=fields.Date.today() )
    # @api.onchange('date')
    # def onchange_date(self):
    #     if self.date:
    #         create_group_name = self.env['res.groups'].search(
    #             [('name', '=', 'Unlock_Date')])
    #         result = self.env.user.id in create_group_name.users.ids
    #         if result == False:
    #             if datetime.strptime(str(self.date), DEFAULT_SERVER_DATE_FORMAT).date() < datetime.now().date():
    #                 self.update({
    #                     'date': False
    #                 })
    #                 raise ValidationError('Please select a date equal/or greater than the current date')

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('approved', 'Approved') ], required=False ,default='draft')
    name = fields.Char(string="Number", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,domain=[('type', 'in', ['bank','cash'])],  )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=True, )
    is_select_all = fields.Boolean(string="Select All",  )
    loan_line= fields.One2many('loan.line.rs.wizard', 'loan_id')
    total_amount = fields.Float(string="Total Amount",compute="_compute_total_amount",  required=False, )
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    start_cheque = fields.Integer(string="Start", required=False, )
    end_cheque = fields.Integer(string="End", required=False, )
    type = fields.Selection(selection=TYPE_SELECTION, related='journal_id.type', store=True, string='Payment Type')
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                              ('bank', 'Bank'),
                              ],default="cheque")

    def update_bank_data(self):
        counter = self.start_cheque
        print("counter :: %s",counter)
        for line in self.loan_line:
            line.bank_name = self.bank_name.id
            if self.end_cheque >= counter:
                line.cheque = counter
                counter +=1
    def _compute_total_amount(self):
        for rec in self:
            if rec.is_select_all == True:
                for line in rec.loan_line:
                    rec.total_amount += line.amount
            else:
                for line in rec.loan_line:
                    if line.is_pay == True:
                        rec.total_amount += line.amount
                    else:
                        rec.total_amount += 0
    @api.onchange('reservation_id')
    def onchange_reservation_id(self):
        if self.reservation_id:
            loan_lines=[]
            for line in self.reservation_id.payment_strg_ids:
                print("line.id :: %s",line.id)
                strg = self.env['payment.strg'].sudo().search([
                    ('id', '=', line.id)
                ], limit=1)
                print(" strg:: %s",strg)

                if not line.is_pay :
                    if line.state_payment == self.state_payment:
                        loan_lines.append((0,0,
                                           {
                                               'payment_date':line.payment_date,
                                               'amount':line.amount,
                                               'description':line.description,
                                               'installment_line_id': line.id,
                                               'payment_strg_id': strg,
                                               'name':line.name,
                                               'cus_bank':line.cus_bank,
                                               'bank_name':line.bank_name,
                                               'cheque': line.cheque,
                                               'amount_due':line.amount_due,
                                               'is_main': line.is_maintainance,
                                               'state_payment': line.state_payment
                                           }))
            # self.partner_id=self.reservation_id.customer_id.id
            self.loan_line = [(6,0,[])]
            self.loan_line=loan_lines

    # create method
    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('customer.payment.seq')
        return super(Customer_payment, self).create(values)

    @api.onchange('is_select_all')
    def onchange_method_is_select_all(self):
        if self.is_select_all == True:
            for line in  self.loan_line:
                line.is_pay = True
        else:
            for line in  self.loan_line:
                line.is_pay = False
    def approved(self):
        if self.is_select_all == False:
            flag = 0
            for line in  self.loan_line:
                if line.is_pay == True:
                    flag = 1

            if flag == 0:
                raise ValidationError(_(
                    "Sorry .. you must Select once one payment !!"))

        account_payment = self.env['account.payment']
        data_bank = self.env['data.bank.cheque']

        self.state = 'approved'
        if self.is_select_all == True:
            for line in  self.loan_line:
                 if line.amount > line.amount_due:
                    raise UserError(_("You Cant Payment begger than amount due."))
                 if line.type == 'bank':
                     method = self.env['account.payment.method'].sudo().search([
                         ('name', '=', 'Batch Deposit')
                     ], limit=1)
                     if line.bank_name.id == False:
                         raise UserError(_("You Must Add Bank Name."))
                     if line.cheque == False:
                         raise UserError(_("You Must Add Cheque Number."))

                 else:
                     method = self.env['account.payment.method'].sudo().search([
                         ('name', '=', 'Manual')
                     ], limit=1)
                 # method = self.env['account.payment.method'].sudo().search([
                 #    ('name', '=', 'Batch Deposit')
                 #    ],limit=1)
                 pay_strg = self.env['payment.strg'].sudo().search([
                     ('id', '=', line.installment_line_id)
                 ], limit=1)


                 print("line.is_main :> ",line.is_main)
                 pay =  account_payment.create({
                     'payment_type':'inbound',
                     'partner_type':'customer',
                     'partner_id': self.partner_id.id,
                     'journal_id': self.journal_id.id,
                     'amount': line.amount,
                     'payment_date': fields.Date.today(),
                     'communication': self.name + " -> " + self.reservation_id.name,
                     'payment_method_id': method.id,
                     'bank_name': line.bank_name.name,
                     'check_number':line.cheque,
                     'due_date': line.payment_date,
                     'actual_date': line.payment_date,
                     'reservation_id': self.reservation_id.id,
                     'custoemr_payment_id': self.id,
                     'payment_strg_id': pay_strg.id,
                     'is_contract': True,
                     'is_main': line.is_main,

                 })
                 data_bank_id = data_bank.create({
                     'bank_id': line.bank_name.id,
                     'cheque_number': line.cheque,
                     'reservation_id': self.reservation_id.id,
                     'payment_id': pay.id,

                 })
                 l = []
                 p = []
                 l.append(data_bank_id.id)
                 for line2 in pay_strg.bank_ids:
                     l.append(line2.id)
                 p.append(pay.id)
                 for rec in pay_strg.payments_ids:
                     p.append(rec.id)
                 pay_strg.update({
                     'bank_ids': [(6, 0, l)],
                     'payments_ids': [(6, 0, p)],
                 })
                 # pay_strg = self.env['payment.strg'].sudo().search([
                 #     ('id', '=', line.installment_line_id)
                 # ], limit=1)
                 print("enter 1")
                 if line.amount == pay_strg.amount_due:
                     print("enter 2")
                     if line.amount == pay_strg.base_amount:
                         print("enter 3")
                         pay_strg.update({
                             'is_pay': True,
                             'amount_pay': pay_strg.amount_pay + line.amount,
                             'amount' : pay_strg.base_amount,
                         })
                     else:
                         print("enter 4")
                         if line.amount == pay_strg.amount_due:
                             pay_strg.update({
                                 'is_pay': True,
                                 'amount_pay': pay_strg.amount_pay + line.amount,
                                 'amount' : pay_strg.base_amount,
                             })
                         else:
                             pay_strg.update({
                                 'is_part': True,
                                 'amount_pay': pay_strg.amount_pay + line.amount,
                                 'amount': pay_strg.base_amount,
                             })
                 else:
                     print("enter 5")
                     if line.amount == pay_strg.amount_due:
                         print("enter 6")
                         pay_strg.update({
                             'is_pay': True,
                             'amount_pay': pay_strg.amount_pay + line.amount,
                             'amount': pay_strg.base_amount,
                         })
                     else:
                         print("enter 7")
                         pay_strg.update({
                             'is_part': True,
                             'amount_pay': pay_strg.amount_pay + line.amount,
                             'amount': pay_strg.base_amount,
                         })
                 print("pay_strg :: %s",pay_strg.id)
                 print("pay :: %s",pay)
                 print("pay :: %s",pay.state)
                 if pay:
                    pay.post()
        else:
            for line in  self.loan_line:

                 method = self.env['account.payment.method'].sudo().search([
                    ('name', '=', 'Batch Deposit')
                    ],limit=1)
                 if line.is_pay == True:
                     if line.amount > line.amount_due:
                         raise UserError(_("You Cant Payment begger than amount due."))
                     pay2 = account_payment.create({
                         'state':'draft',
                         'payment_type':'inbound',
                         'partner_type':'customer',
                         'partner_id': self.partner_id.id,
                         'journal_id': self.journal_id.id,
                         'amount': line.amount,
                         'payment_date': line.payment_date,
                         'communication': self.reservation_id.name,
                         'payment_method_id': method.id,
                         'bank_name': line.bank_name.name,
                         'check_number':line.cheque,
                         'due_date': line.payment_date,
                         'actual_date': line.payment_date,
                         'reservation_id': self.reservation_id.id,
                         'custoemr_payment_id': self.id,
                         'payment_strg_id': line.payment_strg_id.id,
                         'is_contract': True,
                     'is_main': line.is_main,



                     })
                     # print("pay :: ")
                     pay_strg = self.env['payment.strg'].sudo().search([
                         ('id', '=', line.installment_line_id)
                     ], limit=1)
                     data_bank_id = data_bank.create({
                         'bank_id': line.bank_name.id,
                         'cheque_number': line.cheque,
                         'reservation_id': self.reservation_id.id,
                         'payment_id': pay2.id,

                     })
                     l = []
                     p = []
                     l.append(data_bank_id.id)
                     for line2 in pay_strg.bank_ids:
                         l.append(line2.id)
                     p.append(pay2.id)
                     for rec in pay_strg.payments_ids:
                         p.append(rec.id)

                     pay_strg.update({
                         'bank_ids': [(6, 0, l)],
                         'payments_ids': [(6, 0, p)],
                     })
                     if line.amount == pay_strg.amount_due:
                         if line.amount == pay_strg.base_amount:
                             pay_strg.update({
                                 'is_pay': True,
                                 'amount_pay': pay_strg.amount_pay + line.amount,
                                 'amount': pay_strg.base_amount,
                             })
                         else:
                             pay_strg.update({
                                 'is_part': True,
                                 'amount_pay': pay_strg.amount_pay + line.amount,
                                 'amount': pay_strg.base_amount,
                             })
                     else:
                         if line.amount == pay_strg.amount_due:
                             pay_strg.update({
                                 'is_pay': True,
                                 'amount_pay': pay_strg.amount_pay + line.amount,
                                 'amount': pay_strg.base_amount,
                             })
                         else:
                             pay_strg.update({
                                 'is_part': True,
                                 'amount_pay': pay_strg.amount_pay + line.amount,
                                 'amount': pay_strg.base_amount,
                             })
                     print("pay_strg ::3333 %s", pay_strg.id)
                     print("pay2 ::3333 %s", pay2.state)
                     if pay2.state == 'draft':
                        pay2.post()

    number_ins = fields.Integer(string="", required=False, compute="_compute_number_ins")


    def _compute_number_ins(self):
        for rec in self:
            if rec.loan_line:
                rec.number_ins = len(rec.loan_line)
            else:
                rec.number_ins = 0


class loan_line_rs_wizard(models.Model):
    _name = 'loan.line.rs.wizard'

    loan_id= fields.Many2one('customer.payment', ondelete='cascade', readonly=True)
    res_id= fields.Many2one('res.reservation')
    installment_line_id= fields.Integer('id ')
    payment_strg_id = fields.Many2one(comodel_name="payment.strg", string="Payment Strg", required=False, )
    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string='Customer', )
    project_id = fields.Many2one('project.project', string='Project', )
    payment_date = fields.Date(_('Date'))
    amount = fields.Float(_('Amount'), digits=(16, 6))
    amount_due = fields.Float(_('Amount Due'), digits=(16, 6) ,store=True)
    description = fields.Char(_('Description'))
    move_check = fields.Boolean(string='Paid')
    cus_bank = fields.Many2one('payment.bank.cus', _("Customer Bank Name"))
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    cheque = fields.Char(_("Cheque Number"))
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', oldname="payment_method")
    is_pay = fields.Boolean(string="Is Pay",  )
    cheque = fields.Char(_("Cheque Number"))
    type = fields.Selection(selection=TYPE_SELECTION, related='loan_id.type', store=True, string='Payment Type')
    is_main = fields.Boolean(string="",  )
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                              ('bank', 'Bank'),
                              ],default="cheque")