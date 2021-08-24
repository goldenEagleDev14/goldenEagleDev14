# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError

import logging

LOGGER = logging.getLogger(__name__)

class TransferUnit(models.Model):
    _name = 'transfer.unit'
    _description = "Transfer Unit"

    date = fields.Date(string="Date", required=True,default=fields.Date.today() )

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('approved', 'Approved') ], required=False ,default='draft')
    name = fields.Char(string="Number", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True, )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Release Reservation", required=True )
    # reservation_id = fields.Many2one(comodel_name="res.reservation", string="Release Reservation", required=True,domain=[('state', '=', 'reserved')] )
    reservation_id_2 = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=True )
    # reservation_id_2 = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=True,domain=[('state', '=', 'reserved')] )
    # unit
    property_id = fields.Many2one(related="reservation_id.property_id",comodel_name="product.product", string="Unit", required=False, )
    property_id_2 = fields.Many2one(related="reservation_id_2.property_id",comodel_name="product.product", string="Unit", required=False, )
    net_price = fields.Float(related="reservation_id.net_price",string="Net Price")

    is_select_all = fields.Boolean(string="Select All",  )
    payments_post_ids = fields.One2many(comodel_name="account.payment", inverse_name="transfer_post_id", string="", required=False, )
    payments_collected_ids = fields.One2many(comodel_name="account.payment", inverse_name="transfer_collected_id", string="", required=False, )
    payments_post_res1_ids = fields.Many2many(comodel_name="account.payment", relation="payment_post", column1="payment1", column2="post", string="Payments ( Posted )", )
    amount_post = fields.Float(string="Total Amount",  required=False,compute="_compute_payment_post" )
    def _compute_payment_post(self):
        for rec in self:
            amount = 0
            if rec.payments_post_res1_ids:
                for line in rec.payments_post_res1_ids:
                    amount += line.amount

                rec.amount_post = amount
            else:
                rec.amount_post = amount
    payments_collected_res2_ids = fields.Many2many(comodel_name="account.payment", relation="payment_collected", column1="payment2", column2="collected", string="Payments ( Collected )", )
    amount_collected = fields.Float(string="Total Amount", required=False, compute="_compute_payment_collected")

    def _compute_payment_collected(self):
        for rec in self:
            amount = 0
            if rec.payments_collected_res2_ids:
                for line in rec.payments_collected_res2_ids:
                    amount += line.amount

                rec.amount_collected = amount
            else:
                rec.amount_collected = amount
    @api.onchange('reservation_id_2')
    def onchange_method_reservation_id_2(self):
        if self.reservation_id_2:
            ids = []
            for line in self.reservation_id_2.payment_strg_ids:
                    for line2 in line.payments_ids:
                        if line2.state in  ['posted','refunded_under_collection']:
                            ids.append(line2.id)

            pays = self.env['account.payment'].search([('id', '=', ids),
                                                              ])
            print("pays :: %s",pays)
            self.update({
                'payments_post_res1_ids':[(6,0,pays.ids)],
                'payments_post_ids':[(6,0,pays.ids)],
            })


    @api.onchange('reservation_id')
    def onchange_method_reservation_id(self):
        if self.reservation_id:
            ids = []
            for line in self.reservation_id.payment_strg_ids:
                    for line2 in line.payments_ids:
                        if line2.state == 'collected':
                            ids.append(line2.id)

            pays = self.env['account.payment'].search([('id', '=', ids),
                                                              ])
            print("pays :: %s",pays)
            self.update({
                'payments_collected_res2_ids':[(6,0,pays.ids)],
                'payments_collected_ids':[(6,0,pays.ids)],
            })


    @api.model
    def create(self, values):

        values['name'] = self.env['ir.sequence'].next_by_code('transfer.unit.seq')
        return super(TransferUnit, self).create(values)

    # data entry
    post_data = fields.Date(string="Refund Data", required=False, )
    post_data_2 = fields.Date(string="Refund Data", required=False, )
    collect_data = fields.Date(string="Collect Date", required=False, )
    journal_miscellaneous_id = fields.Many2one(comodel_name="account.journal",domain=[('type','=','general')], string="", required=False, )

    def approved(self):
        for rec in self:
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
            ids_post = []
            for p in rec.payments_post_res1_ids:
                print('rrrrrrrrrrrrrrrrrr')
                ids_post.append(p.id)

            for line in rec.reservation_id_2.payment_strg_ids:
                for p in line.payments_ids:
                    if p.id in ids_post:
                        print('ssssssssssssssss')
                        line.amount_pay = 0
                        line.amount_due = line.amount

            ids_p = []
            if rec.amount_post >= rec.amount_collected:
                print('ids_post',ids_post)
                for line in rec.reservation_id_2.payment_strg_ids:
                     for l in line.payments_ids:
                         if l.id in ids_post:
                            ids_p.append(line.id)
                print('ids_p',ids_p)
                for c in rec.payments_collected_res2_ids:
                    total_sum_collected = c.amount
                    print('ggggggg')
                    for line in rec.reservation_id_2.payment_strg_ids:
                        if line.id in ids_p:
                            print("ttttt")
                            ids = []

                            print('total_sum_collected :: %s', total_sum_collected)
                            if total_sum_collected > 0:
                                print('total_sum_collected :: %s',total_sum_collected)
                                if line.amount != line.amount_pay:
                                    print('remainder ::', line.amount)
                                    print('remainder ::', line.amount_pay)
                                    remainder = line.amount - line.amount_pay
                                    if total_sum_collected > remainder:
                                        print('remainder ::',remainder)

                                        total_sum_collected -= remainder
                                        ids.append(c.id)
                                        line.amount_pay = line.amount_pay + remainder
                                    else:
                                        line.amount_pay = line.amount_pay + total_sum_collected
                                        total_sum_collected = 0
                                        ids.append(c.id)


                            for li in line.payments_ids:
                                ids.append(li.id)
                                if li.state == 'posted':
                                    li.move_date = fields.Date.today()
                                    li.multi_select = True
                                    li.refund_notes(ref_notes_batch=1)
                                    li.collected_by = c.id
                            line.payments_ids = [(6,0,ids)]

            else:
                raise ValidationError('Please select a Payment Post equal/or greater than the current Payments Collected')

            rec.state = 'approved'
            rec.reservation_id.state = 'transfer'
            rec.reservation_id.property_id.state = 'available'