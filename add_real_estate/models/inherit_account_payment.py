from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError

class AccountPayment(models.Model):
    _inherit = "account.payment"


    vendor_normal_id = fields.Many2one('vendor.normal.deposit', ondelete='set null', copy=False)

    reservation_id = fields.Many2one(comodel_name="res.reservation", string="", required=False,readonly=True )
    broker_id = fields.Many2one(related="reservation_id.broker_id",comodel_name="res.partner", string="Broker", required=False, )

    request_id = fields.Many2one(comodel_name="request.reservation", string="", required=False,readonly=True )
    property_id = fields.Many2one(related="reservation_id.property_id", comodel_name="product.product",string="Unit", required=False, )
    state_property_id = fields.Selection([('draft', _('Draft')),('request_available', _('Request Available')),('approve', _('Approve')),('available', _('Available')),
                               ('reserved', _('Reserved')),('contracted', _('Contracted')),
                               ('blocked', _('Blocked')),
                              ('exception',_('Exception'))],related="property_id.state" ,string="Status", default='draft', copy=False)
    custoemr_payment_id = fields.Many2one(comodel_name="customer.payment", string="Customer Payment", required=False,readonly=True )
    payment_strg_request_id = fields.Many2one(comodel_name="payment.strg.request", string="Payment Strg Request", required=False, )
    payment_strg_id = fields.Many2one(comodel_name="payment.strg", string="Payment Strg", required=False, )
    is_contract = fields.Boolean(string="Is Contract", readonly=True )
    parent_id_split = fields.Many2one(comodel_name="account.payment", string="Parent", required=False, )
    split_amount = fields.Float(string="",  required=False,compute="_compute_split_amount" )
    remaining_amount = fields.Float(string="Remaining Splitting",  required=False,compute="_compute_split_amount" )
    ref_coll_vendor = fields.Date(string="[Refund/withdrawal] Date")

    is_payment_lines = fields.Boolean(string="Is Payment Lines",  )
    def _compute_split_amount(self):
        print("here come")
        for line in self:
            payment_obj = self.env['account.payment']
            payment = payment_obj.search([('parent_id_split', '=', line.id)])
            total = 0
            print("payment :: ",payment)
            if payment:
                for p in payment:
                    total += p.amount
                line.split_amount = total
                line.remaining_amount = line.amount - total
            else:
                line.split_amount = 0
                line.remaining_amount = 0

    collected_by = fields.Many2one(comodel_name="account.payment", string="Collected By", required=False, )
    transfer_post_id = fields.Many2one(comodel_name="transfer.unit", string="", required=False, )
    transfer_collected_id = fields.Many2one(comodel_name="transfer.unit", string="", required=False, )
    is_main = fields.Boolean(string="",readonly=True  )
    def refund_payable(self,refund2=None):
        """"
            refunded of send check moves

        """""

        refund = self._context.get('refund')
        if refund2 == 1:
            refund = refund2
        refund_delivery = self._context.get('refund_delivery')

        if refund:

            if not self.refund_date:
                raise ValidationError('Please Enter Refund Date')
            if self.state not in ['posted']:
                raise ValidationError(
                    "Can't create reverse entry for this payment since it's not in post or refunded from under collection state")
            if self.partner_type != 'customer':
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('debit', '>', 0), ('move_id.ref', 'not ilike', 'reversal of:'),
                     ('account_id', '=', self.partner_id.property_account_payable_id.id)])
            else:
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('debit', '>', 0), ('move_id.ref', 'not ilike', 'reversal of:'),
                     ('account_id', '=', self.partner_id.property_account_receivable_id.id)])

            aml_rec = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('debit', '>', 0),
                 ('move_id.ref', 'not ilike', 'reversal of:')])

            for j in aml_rec:
                if self.state == 'refunded_under_collection':
                    break
                if j.debit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('debit_move_id', '=', j.id)])
                if j.credit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('credit_move_id', '=', j.id)])
                if reconciled:
                    raise ValidationError(
                        "A reconciled action has done for this payment unreconcile it to complete refund action")

            move = self.env['account.move'].browse(aml.move_id.id)
            default_values_list = []
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>MOVEEEE ", move)

            default_values_list.append({
                'ref': _('Reversal of: %s') % (move.name),
                'date': self.refund_date or self.move_date or self.actual_date,
                'journal_id': aml.journal_id.id,
            })

            move = move._reverse_moves(
                default_values_list)

            # move.reverse_moves(
            #     self.refund_date or self.move_date or self.actual_date,
            #     aml.journal_id or False)

            # move = self.env['account.move'].browse(move.id)
            for k in move.line_ids:
                k.payment_id = self.id
            move.action_post()
            self.state = 'check_refund'
            self.hide_bank = True
            self.hide_del = True
            return True

        if refund_delivery:
            if not self.refund_delivery_date:
                raise ValidationError('Please Enter Deliver Refund Date')
            if self.state not in ['deliver']:
                raise ValidationError(
                    "Can't Create Reverse Entry For This Payment Since It's Not In Post or Refunded From Under collection State")

            self.hide_del = False
            aml = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('credit', '>', 0), ('move_id.ref', 'not ilike', 'reversal of:'),
                 ('account_id', '=', self.journal_id.deliver_account.id)])

            aml_rec = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('debit', '>', 0),
                 ('move_id.ref', 'not ilike', 'reversal of:')])

            for j in aml_rec:
                if self.state == 'refunded_under_collection':
                    break
                if j.debit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('debit_move_id', '=', j.id)])
                if j.credit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('credit_move_id', '=', j.id)])
                if reconciled:
                    raise ValidationError(
                        "A reconciled action has done for this payment unreconcile it to complete refund action")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", aml)
            move = self.env['account.move'].browse(aml[0].move_id.id)
            default_values_list = []
            default_values_list.append({
                'ref': _('Reversal of: %s,') % (move.name,),
                'date': self.refund_delivery_date or self.actual_date,
                # 'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                'journal_id': aml[0].journal_id.id,
            })

            move = move._reverse_moves(
                default_values_list)

            # move.reverse_moves(
            #     self.refund_delivery_date or self.actual_date,
            #     aml[0].journal_id or False)

            # move = self.env['account.move'].browse(move)
            for k in move.line_ids:
                k.payment_id = self.id
            move.action_post()
            self.state = 'posted'
            return True

    def refund_notes(self,ref_und_coll_batch=None,ref_notes_batch=None):
        print("hererhererererer refund_notes")
        print("ref_und_coll_batch ::%s",ref_und_coll_batch)
        print("ref_notes_batch ::%s",ref_notes_batch)
        """""
            refunded of receive check moves 

        """""
        if self.reservation_id:
            if self.is_payment_lines == True:
                self.reservation_id.payment_lines -= self.amount

        refund_notes_batch = self._context.get('ref_notes_batch')
        if ref_notes_batch == 1:
            refund_notes_batch = ref_notes_batch
        refund_under_collect_batch = self._context.get('ref_und_coll_batch')
        if ref_und_coll_batch == 1:
            refund_under_collect_batch = ref_und_coll_batch
        print("refund_notes_batch %s",refund_notes_batch)
        print("refund_under_collect_batch %s",refund_under_collect_batch)
        if refund_notes_batch:

            if not self.move_date:
                raise ValidationError('Please Enter Refund Notes Date')
            else:

                if self.state not in ['posted', 'refunded_under_collection']:
                    raise ValidationError(
                        "Can't create reverse entry for this payment since it's not in post or refunded from under collection state")
                # aml = self.move_line_ids.filtered(
                #     lambda r: r.debit > 0
                #     )
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('debit', '>', 0), ('name', '=', 'Receive Money (Batch Deposit)'),
                     ('move_id.ref', 'not ilike', 'reversal of:')])

                # aml_rec = self.move_line_ids.filtered(
                #     lambda r: r.credit > 0
                #     )
                aml_rec = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('credit', '>', 0),
                     ('move_id.ref', 'not ilike', 'reversal of:')])

                for j in aml_rec:
                    if self.state == 'refunded_under_collection':
                        break
                    if j.debit > 0:
                        reconciled = self.env['account.partial.reconcile'].search([('debit_move_id', '=', j.id)])
                    if j.credit > 0:
                        reconciled = self.env['account.partial.reconcile'].search([('credit_move_id', '=', j.id)])
                    if reconciled:
                        raise ValidationError(
                            "A reconciled action has done for this payment unreconcile it to complete refund action")

                default_values_list = []

                move = self.env['account.move'].browse(aml.move_id.id)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>MOVE  ", move)

                default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,),
                    # 'date': self.actual_date or move.actual_date,
                    'date': self.move_date or self.actual_date,
                    # 'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                    'journal_id': aml.journal_id.id,
                })

                move = move._reverse_moves(
                    default_values_list)

                move = self.env['account.move'].browse(move.id)

                for k in move.line_ids:
                    k.payment_id = self.id
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>After reserve ", k, k.payment_id)

                move.action_post()
                self.state = 'refunded_from_notes'
                return True
        if refund_under_collect_batch:
            if not self.ref_coll_batch:
                raise ValidationError('Please Enter Refunded Date')
            else:
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('name', '=', 'Under collection')], limit=1)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AML ", aml)
                default_values_list = []

                move = self.env['account.move'].browse(aml[0].move_id.id)
                print("move :: %s ",move)
                default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,),
                    # 'date': self.actual_date or move.actual_date,
                    'date': self.ref_coll_batch or self.actual_date,
                    # 'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                    'journal_id': aml[0].move_id.journal_id.id,
                })

                move = move._reverse_moves(
                    default_values_list)
                # move = self.env['account.move'].browse(move.id)

                for k in move.line_ids:
                    k.payment_id = self.id
                move.action_post()
                print("self.state ::--> %s",self.state)
                self.state = 'refunded_under_collection'
                print("self.state ::--> %s",self.state)
                print("self.id ::--> %s",self.id)
                return True



    def post(self):
        res = super(AccountPayment, self).post()
        if self.reservation_id:
            if  self.is_payment_lines == True:
                self.reservation_id.payment_lines += self.amount


        return res