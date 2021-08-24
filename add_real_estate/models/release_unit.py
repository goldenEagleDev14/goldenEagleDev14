# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError

import logging

LOGGER = logging.getLogger(__name__)

class ReleaseUnit(models.Model):
    _name = 'release.unit'
    _description = "Release Unit"

    date = fields.Date(string="Date", required=True,default=fields.Date.today() )

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('approved', 'Approved') ], required=False ,default='draft')
    name = fields.Char(string="Number", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,domain=[('type', 'in', ['bank','cash'])],  )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=True,domain=[('state', '=', 'reserved')] )
    # unit
    property_id = fields.Many2one(related="reservation_id.property_id",comodel_name="product.product", string="Unit", required=False, )
    net_price = fields.Float(related="reservation_id.net_price",string="Net Price")

    release_partner_id = fields.Many2one(comodel_name="res.partner", string="Release Partner", required=True, )
    is_select_all = fields.Boolean(string="Select All",  )

    total_amount = fields.Float(string="Total Amount",  required=False,compute="_compute_amount" )
    amount_due = fields.Float(string="Amount Due",  required=False,compute="_compute_amount" )
    def _compute_amount(self):
        amount = 0
        for rec in self:
            payment_collected = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', '=', 'collected'),
            ])
            payment_open = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', 'in', ['posted', 'under_coll'])
            ])
            for line in payment_collected:
                amount += line.amount
            rec.total_amount = rec.net_price
            rec.amount_due = rec.net_price -  amount

    lines_ids = fields.One2many(comodel_name="release.payment.line", inverse_name="release_id", string="", required=False, )
    @api.onchange('reservation_id')
    def onchange_method_reservation_id(self):
        for rec in self:
            release_payment_line = self.env['release.payment.line']
            print("here")
            payment_collected = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', '=', 'collected'),
            ])
            payment_open = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', 'in', ['posted','under_coll'])
            ])
            if payment_collected:
                for line in payment_collected:
                    release_payment_line.create({
                        'date': line.payment_date,
                        'state': line.state,
                        'name': line.name,
                        'journal_id': line.journal_id.id,
                        'amount': line.amount,
                        'reservation_id':line.reservation_id.id,
                        'release_id': rec.id,
                    })

            if payment_open:
                for line in payment_open:
                    release_payment_line.create({
                        'date': line.payment_date,
                        'state': line.state,
                        'name': line.name,
                        'journal_id': line.journal_id.id,
                        'amount': line.amount,
                        'release_id': rec.id,
                    })
    # @api.model
    # def create(self, values):
    #     values['name'] = self.env['ir.sequence'].next_by_code('release.unit.seq')
    #     res= super(ReleaseUnit, self).create(values)
    #     return  res

    @api.onchange('is_select_all')
    def onchange_method_is_select_all(self):
        print('ffffffff')
    payments_count = fields.Integer(compute='_compute_payment_count', string="Payment Count")

    def _compute_payment_count(self):
        for rec in self:
            release_payment_line = self.env['release.payment.line']
            print("here")
            payment_collected = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
            ])
            rec.payments_count = len(payment_collected)


    def action_view_payment(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_payment_info_all_2').read()[0]
        print("action %s",action)
        context = {
            'default_reservation_id': self.reservation_id.id,
            'default_partner_id': self.partner_id.id,
        }
        # domain = {
        #     'reservation_id': self.reservation_id.id,
        #     'partner_id': self.partner_id.id,
        # }
        action['domain'] = [('reservation_id', '=', self.reservation_id.id),('partner_id', '=', self.partner_id.id),]

        # action['domain'] = domain
        action['context'] = context
        print("action['context'] %s",action['context'])
        print("action['context'] %s",action['domain'])

        return action

    @api.model
    def create(self, values):

        values['name'] = self.env['ir.sequence'].next_by_code('release.unit.seq')
        return super(ReleaseUnit, self).create(values)

    new_reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=False, )
    move_id = fields.Many2one(comodel_name="account.move", string="Move", required=False, )
    post_data = fields.Date(string="Refund Data", required=False, )
    post_data_2 = fields.Date(string="Refund Data", required=False, )
    collect_data = fields.Date(string="Collect Date", required=False, )
    journal_miscellaneous_id = fields.Many2one(comodel_name="account.journal",domain=[('type','=','general')], string="", required=False, )

    def approved(self):
        for rec in self:
            print("1")
            payment_collected = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', '=', 'collected'),
            ])
            payment_posted = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', 'in', ['posted'])
            ])
            payment_under_coll = self.env['account.payment'].search([
                ('reservation_id', '=', rec.reservation_id.id),
                ('partner_id', '=', rec.partner_id.id),
                ('state', 'in', ['under_coll'])
            ])
            print("payment_collected :: %s",payment_collected)
            print("payment_posted :: %s",payment_posted)
            print("payment_under_coll :: %s",payment_under_coll)
            amount_col = 0
            for col in payment_collected:
                amount_col += col.amount

            print("amount_col :: %s",amount_col)
            for posted in payment_posted:
                print("entrer post")
                posted.move_date = fields.Date.today()
                posted.multi_select = True
                print("fileds :: %s :: %s"%(posted.move_date,posted.multi_select))
                posted.refund_notes(ref_notes_batch=1)
                print('ay 7aga bs')

            for under in payment_under_coll:
                print("entrer payment_under_coll")
                account_batch_payment = self.env['account.batch.payment'].search([
                    ('id', '=', under.batch_payment_id.id),("state",'=','under_collection')
                ])
                print("account_batch_payment :: %s",account_batch_payment)
                for account_batch in account_batch_payment:
                    for line in account_batch.payment_ids:
                        line.write({
                            'ref_coll_batch': fields.Date.today(),
                            'multi_select': True,
                        })
                    for line in account_batch.payment_ids_rel:
                        # if line.id == under.id:
                            print("enter if")
                            line.write({
                                'ref_coll_batch' : fields.Date.today(),
                                'move_date' : fields.Date.today(),
                                'multi_select' : True,
                            })
                            print("line.ref_coll_batch :: %s",line.ref_coll_batch)
                            print("line.ref_coll_batch :: %s",line.ref_coll_batch)

                    account_batch.refund_under_collections(ref_und_coll_batch=1)

                payment_refunded_under_collection = self.env['account.payment'].search([
                    ('reservation_id', '=', rec.reservation_id.id),
                    ('partner_id', '=', rec.partner_id.id),
                    ('state', 'in', ['refunded_under_collection'])
                ])
                for refunded in payment_refunded_under_collection:
                    refunded.refund_notes(ref_notes_batch=1)
                # under.ref_coll_batch = fields.Date.today()
                # under.multi_select = True
                # under.batch_payment_id.refund_under_collections()
                # under.multi_select = True
                # under.move_date = fields.Date.today()
                # under.batch_payment_id.post_bank_entrie()


            account_move = self.env['account.move']
            writeoff_lines = []
            total_currency = 0.0

            writeoff_lines.append({
                'name': ('Release'),
                'debit': amount_col,
                'credit':  0.0,
                'amount_currency': total_currency,
                # 'currency_id': total_currency and writeoff_currency.id or False,
                'journal_id': rec.journal_miscellaneous_id.id,
                'account_id': rec.partner_id.property_account_receivable_id.id,
                'partner_id': rec.partner_id.id
            })
            writeoff_lines.append({
                'name': ('Release'),
                'debit': 0.0,
                'credit': amount_col,
                'amount_currency': total_currency,
                # 'currency_id': total_currency and writeoff_currency.id or False,
                'journal_id': rec.journal_miscellaneous_id.id,
                'account_id': rec.release_partner_id.property_account_receivable_id.id,
                'partner_id': rec.release_partner_id.id
            })
            move_id = account_move.create({
                'ref': rec.name,
                'date': fields.Date.today(),
                'journal_id': self.journal_miscellaneous_id.id,
                'line_ids':[(0, 0, line) for line in writeoff_lines]

            })

            rec.move_id = move_id
            res_reservation = self.env['res.reservation']
            lines = []
            for line in rec.reservation_id.payment_strg_ids:
                amount_col_line = 0
                ids = []
                for paym in line.payments_ids:
                    if paym.state == "collected":
                        amount_col_line += paym.amount
                        ids.append(paym.id)
                payment_collected_line = self.env['account.payment'].search([
                        ('id', 'in', ids)
                    ])
                ids_b = []
                for bank in line.bank_ids:
                    if bank.payment_id.state == "collected":
                        ids_b.append(bank.id)
                bank_line = self.env['data.bank.cheque'].search([
                        ('id', 'in', ids_b)
                    ])
                lines.append({
                    'description':line.description,
                    'amount': line.amount,
                    'payment_date': line.payment_date,
                    'journal_id': line.journal_id.id,
                    'deposite':line.deposite,
                    'state_payment':line.state_payment,
                    'amount_pay':amount_col_line,
                    'amount_due': line.amount - amount_col_line,
                    'payments_ids': [(6,0,payment_collected_line.ids)],
                    'bank_ids': [(6, 0,bank_line.ids )],

                })

            print("lines : > ",lines)
            res_id = res_reservation.create({
                'custom_type': 'Reservation',
                'date': fields.Date.today(),
                'project_id': rec.reservation_id.project_id.id,
                'phase_id': rec.reservation_id.phase_id.id,
                'property_id': rec.reservation_id.property_id.id,
                'pay_strategy_id': rec.reservation_id.pay_strategy_id.id,
                'customer_id': rec.release_partner_id.id,
                'sale_person_id': rec.reservation_id.sale_person_id.id,
                # 'payment_strg_ids': [(0, 0, line) for line in lines],
                # 'payment_strg_ids': [(6,0,[(0, 0, line) for line in lines])],
                'is_release': True,
                'odoo_reservation_id': rec.reservation_id.id,
                'state': rec.reservation_id.state,

            })
            print("[(0, 0, line) for line in lines] : ",[(0, 0, line) for line in lines])
            res_id.payment_strg_ids = [(0, 0, line) for line in lines]
            print("res_id :> ",res_id)
            rec.new_reservation_id = res_id.id
            rec.reservation_id.state = 'release'
            rec.state = 'approved'



class ReleaseUnitLine(models.Model):
    _name = 'release.payment.line'
    _description = "Release Unit payment line"

    release_id = fields.Many2one(comodel_name="release.unit", string="", required=False, )
    date = fields.Date(string="Date", required=True,default=fields.Date.today() )

    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('deliver', 'Deliver'),
                              ('under_coll', 'Under collection'),
                              ('collected', 'Withdrawal'),
                              ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled'),
                              ('discount', 'Discount'),
                              ('loan', 'Loan'),
                              ('refund_from_discount', "Refund From Discount"),
                              ('refunded_from_notes', 'Refund Notes Receivable'),
                              ('refunded_under_collection', 'Refund Under collection'),
                              ('check_refund', 'Refunded')],
                             readonly=True, default='draft', copy=False, string="Status")
    name = fields.Char(string="Number", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True,domain=[('type', 'in', ['bank','cash'])],  )
    amount = fields.Float(string="",  required=False, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="", required=False,readonly=True )
