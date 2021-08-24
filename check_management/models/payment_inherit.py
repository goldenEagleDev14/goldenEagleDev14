import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PaymentCheque(models.Model):
    _inherit = 'account.payment'

    cheque_books_id = fields.Many2one(comodel_name='cheque.books', domain=lambda self: self.get_cheque_number())

    cheque_number = fields.Integer(copy=False)
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

    due_date = fields.Date()
    actual_date = fields.Date()
    hide_del = fields.Boolean()
    hide_bank = fields.Boolean()
    # active_cheque_number = fields.Integer(related='journal_id.check_next_number')
    active_cheque_number = fields.Char(related='journal_id.check_next_number')
    active_cheque = fields.Boolean()
    # bank_id = fields.Many2one(comodel_name='account.journal')
    bank_name = fields.Char()
    check_number = fields.Char()
    check_type = fields.Many2one('check.type')
    move_date = fields.Date()
    multi_select = fields.Boolean()
    refund_date = fields.Date()
    delivery_date = fields.Date()
    withdrawal_date = fields.Date()
    multi_check_payment = fields.Boolean(related='journal_id.multi_cheque_book')
    cheque_number_rel = fields.Char(compute='get_cheque_number_name')
    refund_delivery_date = fields.Date()
    loan_date = fields.Date()
    ref_coll_batch = fields.Date()
    batch_state = fields.Selection(related='batch_payment_id.state', default='draft')
    refund_notes_date = fields.Date(string='Refund Under collection Date', readonly=True)

    destination_account_id = fields.Many2one('account.account', compute='_compute_destination_account_id', readonly=False,store=False)
    
    @api.onchange('payment_type', 'payment_method_id', 'journal_id')
    def reset_draft_payment(self):
        for rec in self:
            if rec.state == 'draft':
                rec.due_date = False
                rec.actual_date = False
                rec.bank_name = False
                rec.check_number = False

    @api.constrains('payment_type', 'payment_method_id')
    def notes_receivable_payment_journal(self):
        for rec in self:
            if rec.payment_type == 'inbound' and rec.payment_method_code == 'batch_deposit':
                if rec.journal_id.is_notes_receivable == False:
                    raise ValidationError('Payment Journal Is Not Notes Receivable Journal!')

    @api.onchange('multi_check_payment', 'cheque_books_id')
    def get_cheque_number_name(self):
        for rec in self:
            print("self.journal_id :> ",rec.journal_id)
            if rec.journal_id:
                bank_account = rec.journal_id
            else:
                if 'params' in self._context:
                    if 'id' in self._context['params']:
                        obj = self.env['account.payment'].browse(self._context['params']['id'])
                        bank_account = obj.journal_id
            if rec.cheque_books_id:
                print("bank_account :: ",bank_account)
                if not bank_account.multi_cheque_book:
                    if bank_account.cheque_books_ids:
                        cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True][0]
                        if rec.state == 'draft':
                            self.cheque_number_rel = str(rec.active_cheque_number)
                        # elif cheque_book_object.book_state != 'open' and self.state == 'draft':
                        #     self.cheque_number_rel = str(self.active_cheque_number )

                        else:
                            rec.cheque_number_rel = str(rec.cheque_number)
                else:
                    rec.active_cheque_number = rec.cheque_number
            else:
                rec.cheque_number_rel = False
                return False
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.CHECK",rec.cheque_books_id , rec.cheque_number_rel)
        
    @api.onchange('due_date')
    def get_default_actual_date(self):
        if self.due_date:
            self.actual_date = self.due_date

    @api.onchange('cheque_books_id')
    def get_cheque_book(self):
        if self.cheque_books_id:

            self.active_cheque = self.cheque_books_id.activate
        else:

            self.cheque_number = 0

    # @api.onchange('payment_type','journal_id')
    # def default_cheque_book(self):
    #     self.cheque_books_id = None


    def get_cheque_number(self):

        """""
            default domain for cheque book

            :return list of cheque books in the domain depends on the input of journal

        """

        bank_account = False
        if self.journal_id:
            bank_account = self.journal_id
        else:
            if 'params' in self._context:
                if 'id' in self._context['params']:
                    obj = self.env['account.payment'].browse(self._context['params']['id'])
                    bank_account = obj.journal_id

        if bank_account:
            if not bank_account.multi_cheque_book:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True]
                    if cheque_book_object:
                        return [('id', '=', cheque_book_object[0].id)]
            else:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r.id for r in bank_account.cheque_books_ids]
                    return [('id', 'in', cheque_book_object)]

    @api.onchange('payment_method_id', 'journal_id')
    def get_cheque_number_from_onchange(self):

        """""
            default domain for cheque book
            
            :return list of cheque books in the domain depends on the input of journal 
        
        """

        bank_account = False
        if self.journal_id:
            bank_account = self.journal_id
        self.get_cheque_book()

        if bank_account:
            if not bank_account.multi_cheque_book:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True]
                    if cheque_book_object:
                        cheque_book_object = cheque_book_object[0]
                        if cheque_book_object.book_state == 'done' and self.payment_method_code == 'check_printing':
                            raise ValidationError(
                                'The Check Book ({}) Is Ending, Please Deactivate It or Select Another Journal'.format(
                                    cheque_book_object.name))
                        self.update({'cheque_books_id': cheque_book_object.id})
                        return {'domain': {'cheque_books_id': [('id', '=', cheque_book_object.id)]}}
                else:
                    return {'domain': {'cheque_books_id': [('id', '=', -1)]}}

            else:
                if bank_account.cheque_books_ids:
                    cheque_book_object = [r.id for r in bank_account.cheque_books_ids]
                    return {'domain': {'cheque_books_id': [('id', 'in', cheque_book_object)]}}
                else:
                    return {'domain': {'cheque_books_id': [('id', '=', -1)]}}

        else:
            return {'domain': {'cheque_books_id': [('id', '=', -1)]}}

    @api.constrains('cheque_number')
    def get_cheque(self, from_post=False):

        """""
                get cheque number and validate
                                            1 - if cheque used or not
                                            2 - if cheque valid to in multi cheque book's mood
        """
        bank_account = self.journal_id
        if self.payment_method_code == 'manual':
            return False
        if bank_account:

            if not bank_account.multi_cheque_book:
                if bank_account.cheque_books_ids and self.payment_method_code == 'check_printing':
                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.activate == True]
                    if cheque_book_object:
                        cheque_book_object = cheque_book_object[0]
                    else:
                        raise ValidationError(
                            'Please Activate One Check Book or Make Your bank Account ({}) In Multi Check Mood'.format(
                                bank_account.name))
                    bank_account._get_check_next_number()
                    if cheque_book_object.last_use == 0 and from_post:
                        cheque_book_object.last_use = cheque_book_object.start_from
                    else:
                        if self.state == 'draft' and from_post:
                            bank_account.validate_cheque_book()
                            last_u = cheque_book_object.last_use
                            cheque_book_object.write({'last_use': bank_account.check_next_number})

            else:
                if bank_account.cheque_books_ids:

                    cheque_book_object = [r for r in bank_account.cheque_books_ids if r.id == self.cheque_books_id.id][
                        0]

                    if int(self.cheque_number) > cheque_book_object.end_in or int(
                            self.cheque_number) < cheque_book_object.start_from:
                        raise ValidationError(
                            'the number must be in between {} and {}'.format(cheque_book_object.start_from,
                                                                             cheque_book_object.end_in))
                    else:
                        used_cheque_length = self.env['account.payment'].search(
                            [('journal_id', '=', self.journal_id.id),
                             ('cheque_books_id', '=', self.cheque_books_id.id),
                             ('state', 'in', ['posted', 'deliver', 'collected'])]
                        )
                        cheque_book_length = self.cheque_books_id.end_in - self.cheque_books_id.start_from + 1

                        if len(used_cheque_length) == cheque_book_length:
                            raise ValidationError(
                                "{} Is Ending, Please Open New One !".format(self.cheque_books_id.name))

    @api.model
    def create(self, values):
        # Add code here
        if 'cheque_books_id' in values:
            check_id = values['cheque_books_id']
        else:
            check_id = self.cheque_books_id.id
        if 'cheque_number' in values:
            if check_id:
                ap_obj = self.env['account.payment'].search(
                    [('cheque_books_id', '=', check_id), ('cheque_number', '=', int(values['cheque_number'])),
                     ('state', '!=', 'draft')])
                if ap_obj:
                    raise ValidationError('this Check Number is already used or this payment is posted ')

        return super(PaymentCheque, self).create(values)

    #@api.multi
    def write(self, vals):
        for rec in self:
            if 'cheque_books_id' in vals:
                check_id = vals['cheque_books_id']
            else:
                check_id = rec.cheque_books_id.id
            if 'cheque_number' in vals:
                if check_id:
                    ap_obj = rec.env['account.payment'].search(
                        [('cheque_books_id', '=', check_id), ('cheque_number', '=', int(vals['cheque_number'])),
                         ('state', '!=', 'draft')])
                    if ap_obj:
                        raise ValidationError('this Check Number is already used or this payment is posted ')

            for r in rec:
                if r.state == 'draft' and r.payment_method_code != 'check_printing':
                    vals['cheque_books_id'] = None
            if 'batch_payment_id' in vals:
                if vals['batch_payment_id']:
                    bd = self.env['account.batch.payment'].browse(vals['batch_payment_id'])
                    if bd.state != 'draft':
                        raise ValidationError(
                            'you can\'t add new check within this batch deposite since it\'s not in new stage')
            return super(PaymentCheque, self).write(vals)

    @api.onchange('payment_method_id')
    def hide_bank_buttons(self):

        if self.payment_method_code != 'check_printing':
            self.hide_bank = True
            self.hide_del = True

        else:
            self.hide_bank = False
            self.hide_del = False

    def delete_check_from_batch(self):
        if self.batch_payment_id.state == 'draft':
            self.write({'batch_payment_id': False})
        else:
            raise ValidationError('you can\'t delete line in batch not in draft state')

    def refund_payable(self):
        """"
            refunded of send check moves
            
        """""
        refund = self._context.get('refund')
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
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>MOVEEEE ",move)
            
            default_values_list.append({
                    'ref': _('Reversal of: %s') % (move.name) ,
                    'date':  self.refund_date or self.move_date or self.actual_date,
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
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",aml)
            move = self.env['account.move'].browse(aml[0].move_id.id)
            default_values_list = []
            default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,) ,
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

    def refund_notes(self):

        """""
            refunded of receive check moves 
        
        """""


        refund_notes_batch = self._context.get('ref_notes_batch')
        refund_under_collect_batch = self._context.get('ref_und_coll_batch')
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
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>MOVE  ",move)
            
                

                default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,) ,
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
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>After reserve ",k,k.payment_id)
                
                move.action_post()
                self.state = 'refunded_from_notes'
                return True
        if refund_under_collect_batch:
            if not self.ref_coll_batch:
                raise ValidationError('Please Enter Refunded Date')
            else:
                aml = self.env['account.move.line'].search(
                    [('payment_id', '=', self.id), ('name', '=', 'Under collection')], limit=1)
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AML ",aml)
                default_values_list = []
        
                move = self.env['account.move'].browse(aml[0].move_id.id)

                 
                default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,) ,
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
                self.state = 'refunded_under_collection'
                return True

    def refund_discount(self):

        """""
            refunded of Discount check moves 

        """""

        if not self.ref_coll_batch:
            raise ValidationError('Please Enter Refund Date')
        refund_discount_batch = self._context.get('ref_disc_batch')

        if refund_discount_batch:
            if self.state not in ['loan', 'discount']:
                raise ValidationError(
                    "Can't create reverse entry for this payment since it's not in discount or loan state")
            aml = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('debit', '>', 0), ('name', '=', 'Discount Check'),
                 ('move_id.ref', 'not ilike', 'reversal of:')])

            aml_rec = self.env['account.move.line'].search(
                [('payment_id', '=', self.id), ('credit', '>', 0),
                 ('move_id.ref', 'not ilike', 'reversal of:')])

            for j in aml_rec:
                if self.state == 'loan':
                    break
                if j.debit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('debit_move_id', '=', j.id)])
                if j.credit > 0:
                    reconciled = self.env['account.partial.reconcile'].search([('credit_move_id', '=', j.id)])
                if reconciled:
                    raise ValidationError(
                        "A reconciled action has done for this payment unreconcile it to complete refund action")

            move = self.env['account.move'].browse(aml[0].move_id.id)
            default_values_list = []
            default_values_list.append({
                    'ref': _('Reversal of: %s,') % (move.name,) ,
                    'date': self.ref_coll_batch , #self.move_date or self.actual_date,
                    # 'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                    'journal_id': aml[0].journal_id.id,
                })
                
            move = move._reverse_moves(
                    default_values_list)
            # move = move.reverse_moves(self.move_date or self.actual_date,aml[0].journal_id or False)
            # move = self.env['account.move'].browse(move)
            for k in move.line_ids:
                k.payment_id = self.id
            move.action_post()
            self.state = 'refund_from_discount'
            return True

    
    def _prepare_payment_moves(self):
        ''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
        to the 'create' method.

        Example 1: outbound with write-off:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |   900.0   |
        RECEIVABLE          |           |   1000.0
        WRITE-OFF ACCOUNT   |   100.0   |

        Example 2: internal transfer from BANK to CASH:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |           |   1000.0
        TRANSFER            |   1000.0  |
        CASH                |   1000.0  |
        TRANSFER            |           |   1000.0

        :return: A list of Python dictionary to be passed to env['account.move'].create.
        '''
        if self.payment_method_code == 'manual':
            return super(PaymentCheque, self)._prepare_payment_moves()
        all_move_vals = []
        for payment in self:
            liq_move = payment._get_liquidity_move_line_vals(payment.amount)
            
            lig_account_id = self.env['account.account'].browse(liq_move['account_id'])
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ",lig_account_id.name)
            
            company_currency = payment.company_id.currency_id
            move_names = payment.move_name.split(payment._get_move_name_transfer_separator()) if payment.move_name else None

            # Compute amounts.
            write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
            if payment.payment_type in ('outbound', 'transfer'):
                counterpart_amount = payment.amount
                liquidity_line_account = lig_account_id # payment.journal_id.default_debit_account_id
            else:
                counterpart_amount = -payment.amount
                liquidity_line_account = lig_account_id #payment.journal_id.default_credit_account_id

            # Manage currency.
            if payment.currency_id == company_currency:
                # Single-currency.
                balance = counterpart_amount
                write_off_balance = write_off_amount
                counterpart_amount = write_off_amount = 0.0
                currency_id = False
            else:
                # Multi-currencies.
                balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id, payment.payment_date)
                write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id, payment.payment_date)
                currency_id = payment.currency_id.id

            # Manage custom currency on journal for liquidity line.
            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                # Custom currency on journal.
                if payment.journal_id.currency_id == company_currency:
                    # Single-currency
                    liquidity_line_currency_id = False
                else:
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
            else:
                # Use the payment currency.
                liquidity_line_currency_id = currency_id
                liquidity_amount = counterpart_amount

            # Compute 'name' to be used in receivable/payable line.
            rec_pay_line_name = ''
            if payment.payment_type == 'transfer':
                rec_pay_line_name = payment.name
            else:
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Customer Payment")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Customer Credit Note")
                elif payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Vendor Credit Note")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Vendor Payment")
                if payment.invoice_ids:
                    rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

            # Compute 'name' to be used in liquidity line.
            if payment.payment_type == 'transfer':
                liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
            else:
                liquidity_line_name = payment.name

            # ==== 'inbound' / 'outbound' ====
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ",liquidity_line_account.name , payment._get_destination_account_id().name )
            # 1/0
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>|||<<",payment._get_destination_account_id())
            date = False
            if self._context.get('ctx_del',False):
                date = self.delivery_date
            elif self._context.get('ctx_bank',False):
                date = self.withdrawal_date
            elif self._context.get('ctx_del_batch',False):
                date = self.batch_payment_id.date
            elif self._context.get('bank_aml_batch',False):
                date = self.ref_coll_batch
            print(">>>>>>>>>>>>>>>>>>>>>>>>>payment._get_destination_account_id()payment._get_destination_account_id() ",payment._get_destination_account_id())
            move_vals = {
                'date': date or payment.payment_date,
                'ref': payment.communication,
                'journal_id': payment.journal_id.id,
                'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                'partner_id': payment.partner_id.id,
                'line_ids': [
                    # Receivable / Payable / Transfer line.
                    (0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                        'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                        'date_maturity': date or payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment._get_destination_account_id(),
                        'payment_id': payment.id,
                    }),
                    # Liquidity line.
                    (0, 0, {
                        'name': liquidity_line_name,
                        'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                        'currency_id': liquidity_line_currency_id,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'date_maturity': date or payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': liquidity_line_account.id,
                        'payment_id': payment.id,
                    }),
                ],
            }
            if write_off_balance:
                # Write-off line.
                move_vals['line_ids'].append((0, 0, {
                    'name': payment.writeoff_label,
                    'amount_currency': -write_off_amount,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'date_maturity': date or payment.payment_date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': payment.writeoff_account_id.id,
                    'payment_id': payment.id,
                }))

            if move_names:
                move_vals['name'] = move_names[0]

            all_move_vals.append(move_vals)

            # ==== 'transfer' ====
            if payment.payment_type == 'transfer':
                journal = payment.destination_journal_id

                # Manage custom currency on journal for liquidity line.
                if journal.currency_id and payment.currency_id != journal.currency_id:
                    # Custom currency on journal.
                    liquidity_line_currency_id = journal.currency_id.id
                    transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id, payment.payment_date)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    transfer_amount = counterpart_amount

                transfer_move_vals = {
                    'date': payment.payment_date,
                    'ref': payment.communication,
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.destination_journal_id.id,
                    'line_ids': [
                        # Transfer debit line.
                        (0, 0, {
                            'name': payment.name,
                            'amount_currency': -counterpart_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.company_id.transfer_account_id.id,
                            'payment_id': payment.id,
                        }),
                        # Liquidity credit line.
                        (0, 0, {
                            'name': _('Transfer from %s') % payment.journal_id.name,
                            'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.destination_journal_id.default_credit_account_id.id,
                            'payment_id': payment.id,
                        }),
                    ],
                }

                if move_names and len(move_names) == 2:
                    transfer_move_vals['name'] = move_names[1]

                all_move_vals.append(transfer_move_vals)
        return all_move_vals

    def delivery_aml(self):
        self.with_context(delivery_aml=1).post()


    #@api.one
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
                        
                ***********************************************************
                    override in case of used chque payment method
                        add cheque validation 
                        add to different stage 
                                    1 - deliver
                                    2 - collected
        """
        

        if self.payment_method_code == 'manual':
            return super(PaymentCheque, self).post()
        ctx_del = self._context.get('delivery_aml')
        ctx_bank = self._context.get('bank_aml')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>DEEEEEEEEEEEEEELLLLLL ",ctx_del,ctx_bank)
        
        ctx_del_batch = self._context.get('delivery_aml_batch')
        ctx_bank_batch = self._context.get('bank_aml_batch')
        ctx_discount_batch = self._context.get('discount_check')
        collect_discount = self._context.get('collect_disc_batch')
        

        ctx_loan_batch = self._context.get('loan_check')
        if self.cheque_books_id:
            if ctx_del == 1 or ctx_bank == 1:
                pass
            else:

                self.get_cheque(from_post=True)

        if ctx_bank:
            if not self.withdrawal_date:
                raise ValidationError('please Enter Withdrawal Date ...')
            self.hide_bank = True
            self.hide_del = True
        if ctx_del:
            if not self.delivery_date:
                raise ValidationError('please Enter Delivery Date ...')
            self.hide_del = True

        for rec in self:

            if not self.cheque_books_id and not collect_discount and not ctx_loan_batch and not ctx_discount_batch and not ctx_bank and not ctx_del and not ctx_bank_batch and not ctx_del_batch:
                if rec.state not in 'draft':
                    raise UserError(_("Only a draft payment can be posted."))

                if any(inv.state != 'open' for inv in rec.invoice_ids):
                    raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            if ctx_bank_batch:
                if rec.state in ['collected']:
                    return True
            if ctx_del_batch:
                if rec.state in ['collected', 'under_coll']:
                    return True
            # Use the right sequence to set the name
            if rec.cheque_books_id and rec.cheque_number:
                rec.cheque_books_id.book_state = 'open'
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>11")
                rec.cheque_books_id.used_book = True
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>22")
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            if not collect_discount and not ctx_loan_batch and not ctx_discount_batch and not ctx_bank and not ctx_del and not ctx_bank_batch and not ctx_del_batch:
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
                    sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            # amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)

            #TODO:MIG LOAN
            # if ctx_loan_batch:
            #    amount = (self.batch_payment_id.bank_id.bank_id.loan_percentage / 100) * amount
            
            
            # move = rec._create_payment_entry(amount)


            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            
            # if rec.payment_type == 'transfer':
            #     transfer_credit_aml = move.line_ids.filtered(
            #         lambda r: r.account_id == rec.company_id.transfer_account_id)
            #     transfer_debit_aml = rec._create_transfer_entry(amount)
            #     (transfer_credit_aml + transfer_debit_aml).reconcile()

            default_journal_debit_account = False
            default_journal_credit_account = False
            liq_move = self._get_liquidity_move_line_vals(rec.amount)
            

            payment = rec

            if payment.payment_type in ('outbound', 'transfer'):
                # counterpart_amount = payment.amount
                default_journal_debit_account = payment.journal_id.default_debit_account_id
                
                # liquidity_line_account = payment.journal_id.default_debit_account_id

                # payment.journal_id.default_debit_account_id = liq_move['account_id']



                # payment.journal_id.default_debit_account_id = default_journal_debit_account
            else:
                # counterpart_amount = -payment.amount
                default_journal_credit_account = payment.journal_id.default_credit_account_id
                
                # liquidity_line_account = payment.journal_id.default_credit_account_id

                # payment.journal_id.default_credit_account_id = liq_move['account_id']



                # payment.journal_id.default_credit_account_id = default_journal_credit_account

            AccountMove = self.env['account.move'].with_context(default_type='entry')
            dict_val = {'ctx_del':ctx_del,'ctx_bank':ctx_bank,'ctx_del_batch':ctx_del_batch,'ctx_bank_batch':ctx_bank_batch,'ctx_discount_batch':ctx_discount_batch,'collect_discount':collect_discount}
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>dict_valdict_val ",dict_val)
            payment_move_dict = rec.with_context(ctx_del=ctx_del,ctx_bank=ctx_bank,ctx_del_batch=ctx_del_batch,ctx_bank_batch=ctx_bank_batch,ctx_discount_batch=ctx_discount_batch,collect_discount=collect_discount)._prepare_payment_moves()

            #8
            payment_move_dict[0]['journal_id'] = liq_move['journal_id']
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>PREPAER",rec._prepare_payment_moves())
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>payment_move_dict ",payment_move_dict)
            
            move = AccountMove.create(payment_move_dict)
            move.name = '/'
           
            for one_move in move:
                for line in one_move.line_ids:
                    if line.account_id.id == liq_move['account_id']:
                        line.name = liq_move['name']
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>JOR MOV1", line.move_id.state)
                        # line.move_id.journal_id = liq_move['journal_id']
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>JOR MOV2")
                    line.date_maturity = rec.actual_date

            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>JOR MOV3 ",move.name)
            
            move.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()
            
            # move.journal_id.sequence_number_next += 1
            # Update the state / move before performing any reconciliation.
            move_name = self._get_move_name_transfer_separator().join(move.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_type in ('inbound', 'outbound'):
                # ==== 'inbound' / 'outbound' ====
                if rec.invoice_ids:
                    (move[0] + rec.invoice_ids).line_ids \
                        .filtered(lambda line: not line.reconciled and line.account_id.id == rec._get_destination_account_id())\
                        .reconcile()
            elif rec.payment_type == 'transfer':
                # ==== 'transfer' ====
                move.mapped('line_ids')\
                    .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
                    .reconcile()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            ctx_del = self._context.get('delivery_aml')
            ctx_bank = self._context.get('bank_aml')
            

            if ctx_bank_batch:
                rec.write({'state': 'collected'})
                move.data = rec.move_date
            elif ctx_del_batch:
                rec.write({'state': 'under_coll'})
                
                move.data = rec.move_date

            elif ctx_del:
                rec.write({'state': 'deliver'})
            elif ctx_loan_batch:
                rec.write({'state': 'loan'})
            elif ctx_bank or collect_discount:
                rec.write({'state': 'collected'})
            elif ctx_discount_batch:
                rec.write({'state': 'discount'})

            else:
                if self.cheque_books_id:
                    if self.multi_check_payment:
                        rec.write({'state': 'posted'})
                    else:
                        rec.write({'state': 'posted', 'cheque_number': self.active_cheque_number})
                else:
                    rec.write({'state': 'posted', 'cheque_number': self.active_cheque_number})
            # payment.journal_id.default_debit_account_id = default_journal_debit_account
            # payment.journal_id.default_credit_account_id = default_journal_credit_account 
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>||||||",rec,rec.state , ' || ',payment.destination_account_id.name)
           
        # 1/0
        return True

    def _create_payment_entry(self, amount):

        collect_discount = self._context.get('collect_disc_batch')
        if collect_discount:
            return self.create_move_line_collect_discount(amount)
        else:
            return super(PaymentCheque, self)._create_payment_entry(amount)
        return move

    def create_move_line_collect_discount(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
                   Return the journal entry.
               """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            # if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(
            date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,
                                                          invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals())
        loan = (self.batch_payment_id.bank_id.bank_id.loan_percentage / 100) * amount

        discount_check = self.batch_payment_id.bank_id.discount_check_account.id

        if not discount_check:
            raise ValidationError(
                "Your Bank journal {} doesn't have discount check account".format(self.batch_payment_id.bank_id.name))
        counterpart_aml_dict = {'invoice_id': False, 'payment_id': self.id,
                                'amount_currency': False, 'partner_id': self.partner_id.id,
                                'account_id': discount_check,
                                'currency_id': currency_id, 'credit': amount * -1, 'name': 'Collect Loan',
                                'journal_id': move.journal_id.id,
                                'debit': 0.0, 'move_id': move.id}

        # Write line corresponding to invoice payment

        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        # Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:

            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
                self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency
            # minus the payment amount in company currency, and not from the payment difference in the payment currency
            # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount,
                                                                                                         self.company_id.currency_id)
            if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
            # amount in the company currency
            if amount_wo > 0:
                debit_wo = amount_wo
                credit_wo = 0.0
                amount_currency_wo = abs(amount_currency_wo)
            else:
                debit_wo = 0.0
                credit_wo = -amount_wo
                amount_currency_wo = -abs(amount_currency_wo)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or writeoff_line['credit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or writeoff_line['debit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        # Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0

            loan_account = self.batch_payment_id.bank_id.loan_account.id
            bank_account = self.batch_payment_id.bank_id.default_credit_account_id.id
            if not loan_account:
                raise ValidationError(
                    "Your Bank journal {} doesn't have A Loan account".format(loan_account))
            if not bank_account:
                raise ValidationError(
                    "Your Bank journal {} doesn't have defaul credit account".format(bank_account))
            liquidity_aml_dict_1 = {'invoice_id': False, 'payment_id': self.id,
                                    'amount_currency': False, 'partner_id': self.partner_id.id,
                                    'account_id': loan_account,
                                    'currency_id': currency_id, 'credit': 0.0, 'name': 'pay Loan',
                                    'journal_id': move.journal_id.id,
                                    'debit': loan * -1, 'move_id': move.id}

            liquidity_aml_dict_2 = {'invoice_id': False, 'payment_id': self.id,
                                    'amount_currency': False, 'partner_id': self.partner_id.id,
                                    'account_id': bank_account,
                                    'currency_id': currency_id, 'credit': 0.0, 'name': 'collect check amount',
                                    'journal_id': move.journal_id.id, 'debit': (amount * -1) + loan, 'move_id': move.id}

            aml_obj.create(liquidity_aml_dict_1)
            aml_obj.create(liquidity_aml_dict_2)

        # validate the payment
        move.post()

        # reconcile the invoice receivable/payable line(s) with the payment
        self.invoice_ids.register_payment(counterpart_aml)
        return move

    def _get_last_journal(self):
        if self.partner_type == 'customer':
            aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id), ('debit', '>', 0), (
                'account_id', '!=', self.partner_id.property_account_receivable_id.id)])
        else:
            aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id),
                                                             ('credit', '>', 0),
                                                             ('account_id', '!=',
                                                              self.partner_id.property_account_payable_id.id)],order="id desc")

        if aml_objs:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AMLLLLLLLL OBJSSSS",aml_objs)
            return aml_objs[0].account_id.id
        else:
            return False

    def _get_last_journal_batch(self):
        if self.partner_type == 'customer':
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.0")
            if self.payment_method_code == 'batch_payment':
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.1")
                if self.state != 'under_coll':
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.2")
                    aml_objs = self.env['account.move.line'].search(
                        [('payment_id', '=', self.id), ('journal_id', '=', self.journal_id.id), ('debit', '>', 0)])
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.3")
                else:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.4")
                    aml_objs = self.env['account.move.line'].search([('name','ilike','under'),('payment_id', '=', self.id), ('debit', '>', 0)])
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.5")
                last_index = len(aml_objs)-1
                if aml_objs:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.6",aml_objs)
                    return aml_objs[0].account_id.id, aml_objs[0].name
                else:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.7")
                    return False
            else:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.8")
                aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id), ('credit', '>', 0)])
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.9",aml_objs)
                last_index = len(aml_objs)-1
                if aml_objs:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.10")
                    return aml_objs[0].account_id.id, aml_objs[0].name
                else:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.11")
                    return False
        else:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.12")
            if self.payment_method_code == 'batch_payment':

                if self.state != 'under_coll':
                    aml_objs = self.env['account.move.line'].search(
                        [('payment_id', '=', self.id), ('journal_id', '=', self.journal_id.id), ('debit', '>', 0)])
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.13 ",aml_objs)
                    # 1/0
                else:
                    aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id), ('debit', '>', 0)])
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.14 ",aml_objs)
                    # 2/0
                if aml_objs:
                    return aml_objs[0].account_id.id, aml_objs[0].name
                else:
                    return False
            else:
                aml_objs = self.env['account.move.line'].search([('payment_id', '=', self.id), ('debit', '>', 0)])
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.15 ",aml_objs)
                # 3/0
                if aml_objs:
                    return aml_objs[0].account_id.id, aml_objs[0].name
                else:
                    return False

    #@api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id','move_date','move_line_ids')
    def _compute_destination_account_id(self):
        """""
            override _compute_destination_account_id to add 3 different destination if payment method is cheque
                    1-first journal item to payable vendor account
                    2-second one to notes payable accounts from bank account
                    3-third to delivery account from bank account
                    
            
        """
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>||||")
        
        for rec in self:
            ctx_loan_batch = rec._context.get('loan_check')

            des_batch_account = rec._get_last_journal_batch()
            des_account = rec._get_last_journal()
            
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",des_batch_account , ' || ',des_account)

            if rec.invoice_ids and (not des_batch_account or not des_account):
                rec.destination_account_id = rec.invoice_ids[0].account_id.id
            elif rec.payment_type == 'transfer':
                if not rec.company_id.transfer_account_id.id:
                    raise UserError(_('Transfer account not defined on the company.'))
                rec.destination_account_id = rec.company_id.transfer_account_id.id
            elif rec.partner_id:

                if rec.partner_type == 'customer':

                    if rec.payment_method_code == 'batch_payment' and rec._get_last_journal_batch():
                        rec.destination_account_id = des_batch_account[0]
                        print(".>>>>>>>>>>>>>>>>>>>>>>>>>>>>",des_batch_account[0])
                        #run when create debosit and click first multi under collection

                        #also run after second click of approve
                        # 1/0
                    # elif rec.payment_method_code == 'check' :
                    elif rec._get_last_journal_batch():
                        rec.destination_account_id = des_batch_account[0]
                        # 2/0
                    else:
                        rec.destination_account_id = rec.partner_id.property_account_receivable_id.id
                        #run when create payment and click validate
                        # 3/0
                    if ctx_loan_batch:
                        loan_bank = rec.batch_payment_id.bank_id.loan_account.id
                        if not loan_bank:
                            raise ValidationError(
                                "Your Bank journal {} doesn't have A Loan account".format(
                                    rec.batch_payment_id.bank_id.name))
                        rec.destination_account_id = loan_bank
                        # 4/0

                else:

                    if ctx_loan_batch:
                        loan_bank = rec.batch_payment_id.bank_id.loan_account.id
                        if not loan_bank:
                            raise ValidationError(
                                "Your Bank journal {} doesn't have A Loan account".format(
                                    rec.batch_payment_id.bank_id.name))
                        rec.destination_account_id = loan_bank

                    elif rec.cheque_books_id:

                        if des_account:
                            rec.destination_account_id = des_account
                        else:
                            rec.destination_account_id = rec.partner_id.property_account_payable_id.id


                    else:
                        if rec.payment_method_code == 'batch_payment' and rec._get_last_journal_batch():
                            rec.destination_account_id = des_batch_account[0]
                        else:
                            rec.destination_account_id = rec.partner_id.property_account_payable_id.id

    def _get_destination_account_id(self):
        """""
            override _compute_destination_account_id to add 3 different destination if payment method is cheque
                    1-first journal item to payable vendor account
                    2-second one to notes payable accounts from bank account
                    3-third to delivery account from bank account
                    
            
        """
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>||||")
        
        for rec in self:
            ctx_loan_batch = rec._context.get('loan_check')

            des_batch_account = rec._get_last_journal_batch()
            des_account = rec._get_last_journal()
            
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",des_batch_account , ' || ',des_account)

            # if rec.invoice_ids and (not des_batch_account or not des_account):
            #     # rec.destination_account_id = rec.invoice_ids[0].account_id.id
            #     return rec.invoice_ids[0].account_id.id
            if rec.payment_type == 'transfer':
                if not rec.company_id.transfer_account_id.id:
                    raise UserError(_('Transfer account not defined on the company.'))
                # rec.destination_account_id = rec.company_id.transfer_account_id.id
                return rec.company_id.transfer_account_id.id
            elif rec.partner_id:

                if rec.partner_type == 'customer':

                    if rec.payment_method_code == 'batch_payment' and rec._get_last_journal_batch():
                        # rec.destination_account_id = des_batch_account[0]
                        print(".>>>>>>>>>>>>>>>>>>>>>>>>>>>>", des_batch_account[0])
                        # 1/0
                        return des_batch_account[0]
                        # run when create debosit and click first multi under collection

                        # also run after second click of approve

                    # elif rec.payment_method_code == 'check' :
                    elif rec._get_last_journal_batch():
                        # rec.destination_account_id = des_batch_account[0]
                        # 2/0
                        return des_batch_account[0]

                    else:
                        # rec.destination_account_id = rec.partner_id.property_account_receivable_id.id
                        # 3/0
                        return rec.partner_id.property_account_receivable_id.id
                        # run when create payment and click validate

                    if ctx_loan_batch:
                        loan_bank = rec.batch_payment_id.bank_id.loan_account.id
                        if not loan_bank:
                            raise ValidationError(
                                "Your Bank journal {} doesn't have A Loan account".format(
                                    rec.batch_payment_id.bank_id.name))
                        # rec.destination_account_id = loan_bank
                        # 4/0
                        return loan_bank


                else:

                    if ctx_loan_batch:
                        loan_bank = rec.batch_payment_id.bank_id.loan_account.id
                        if not loan_bank:
                            raise ValidationError(
                                "Your Bank journal {} doesn't have A Loan account".format(
                                    rec.batch_payment_id.bank_id.name))
                        # rec.destination_account_id = loan_bank
                        return loan_bank

                    elif rec.cheque_books_id:

                        if des_account:
                            # rec.destination_account_id = des_account
                            return des_account
                        else:
                            # rec.destination_account_id = rec.partner_id.property_account_payable_id.id
                            return rec.partner_id.property_account_payable_id.id


                    else:
                        if rec.payment_method_code == 'batch_payment' and rec._get_last_journal_batch():
                            # rec.destination_account_id = des_batch_account[0]
                            return des_batch_account[0]
                        else:
                            # rec.destination_account_id = rec.partner_id.property_account_payable_id.id
                            return rec.partner_id.property_account_payable_id.id

    def _get_liquidity_move_line_vals(self, amount):

        """""
           override _get_liquidity_move_line_vals to add 3 different source if payment method is cheque
                   1-first journal notes payable accounts from bank account
                   2-second one to delivery account from bank account
                   3-third to default journal debit or credit


       """

        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name

        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound',
                                                'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        if self.cheque_books_id:
            ctx_del = self._context.get('delivery_aml')
            ctx_bank = self._context.get('bank_aml')

            if ctx_del:
                vals = {
                    'name': str(self.cheque_books_id.account_journal_cheque_id.bank_acc_number) + '-' + str(
                        self.cheque_books_id.name) + '-' + str(self.cheque_number),
                    'account_id': self.payment_type in (
                        'outbound') and self.cheque_books_id.account_journal_cheque_id.deliver_account.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }

            elif ctx_bank:
                vals = {
                    'name': str(self.cheque_books_id.account_journal_cheque_id.bank_acc_number) + '-' + str(
                        self.cheque_books_id.name) + '-' + str(self.cheque_number),
                    'account_id': self.payment_type in ('outbound',
                                                        'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }

            else:

                vals = {
                    'name': str(self.cheque_books_id.account_journal_cheque_id.bank_acc_number) + '-' + str(
                        self.cheque_books_id.name) + '-' + str(self.cheque_number),
                    'account_id': self.payment_type in (
                        'outbound') and self.cheque_books_id.account_journal_cheque_id.notes_payable.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
        # If the journal has a currency specified, the journal item need to be expressed in this currency

        if self.payment_method_code == 'batch_payment':
            ctx_del_batch = self._context.get('delivery_aml_batch')
            ctx_bank_batch = self._context.get('bank_aml_batch')
            ctx_discount_batch = self._context.get('discount_check')
            ctx_loan_batch = self._context.get('loan_check')

            if ctx_del_batch:
                if not self.batch_payment_id.bank_id.reveivable_under_collection:
                    raise ValidationError(
                        "Your Bank journal {} doesn't have A Receivable Under collection account".format(
                            self.batch_payment_id.bank_id.name))

                vals = {
                    'name': "Under collection",
                    'account_id': self.batch_payment_id.bank_id.reveivable_under_collection.id,
                    'journal_id': self.batch_payment_id.bank_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
            elif ctx_discount_batch:
                if not self.batch_payment_id.bank_id.discount_check_account:
                    raise ValidationError(
                        "Your Bank journal {} doesn't have A Receivable Discount Check Account account".format(
                            self.batch_payment_id.bank_id.name))

                vals = {
                    'name': "Discount Check",
                    'account_id': self.batch_payment_id.bank_id.discount_check_account.id,
                    'journal_id': self.batch_payment_id.bank_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
            elif ctx_loan_batch:
                if not self.batch_payment_id.bank_id.loan_account:
                    raise ValidationError(
                        "Your Bank journal {} doesn't have A Loan account".format(self.batch_payment_id.bank_id.name))

                vals = {
                    'name': "Receive Loan",
                    'account_id': self.batch_payment_id.bank_id.default_debit_account_id.id,
                    'journal_id': self.batch_payment_id.bank_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
            elif ctx_bank_batch:
                if not self.batch_payment_id.bank_id:
                    raise ValidationError(
                        "Your Register Payment Doesn't Have A Bank To Collect Check In".format(self.journal_id.name))

                vals = {
                    'name': "collection Checks",
                    'account_id': self.batch_payment_id.bank_id.default_debit_account_id.id,
                    'journal_id': self.batch_payment_id.bank_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }


            else:

                vals = {
                    'name': "Receive Money (Batch Deposit)",
                    'account_id': self.payment_type in ('outbound',
                                                        'transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                }
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(
                date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id,
                                                              self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

    def _get_counterpart_move_line_vals(self, invoice=False):

        """"
            override _get_counterpart_move_line_vals to add different label if payment method is cheque
            
        
        """
        ctx_del = self._context.get('delivery_aml')
        ctx_bank = self._context.get('bank_aml')

        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    if ctx_bank or ctx_del:
                        name += str(self.cheque_books_id.account_journal_cheque_id.bank_acc_number) + '-' + str(
                            self.cheque_books_id.name) + '-' + str(self.cheque_number)
                    else:
                        name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name) - 2]

        if self.payment_method_code == 'batch_payment' and self._get_last_journal_batch():
            name = self._get_last_journal_batch()[1]

        return {
            'name': name,
            'account_id': self._get_destination_account_id(),
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

    def _get_move_vals(self, journal=None):

        """ Return dict to create the payment move
        """

        refund = self._context.get('refund')
        refund_delivery = self._context.get('refund_delivery')
        ctx_bank_batch = self._context.get('bank_aml_batch')
        ctx_del_batch = self._context.get('delivery_aml_batch')
        ctx_del = self._context.get('delivery_aml')
        ctx_bank = self._context.get('bank_aml')
        collect_disc_batch = self._context.get('collect_disc_batch')
        loan_check = self._context.get('loan_check')
        discount_all = self._context.get('discount_check')
        refund_discount = self._context.get('refund_discount')
        ref_desc_batch = self._context.get('ref_desc_batch')
        journal = journal or self.journal_id
        if ctx_bank_batch or refund_discount or collect_disc_batch or ctx_del_batch or loan_check or discount_all:
            journal = self.batch_payment_id.bank_id

        if not journal.sequence_id:
            raise UserError(_('The Journal %s Does Not Have A Sequence, Please Specify One.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()

        ref = False

        if self.batch_payment_id:
            ref = self.batch_payment_id.name

        if collect_disc_batch or ref_desc_batch:
            date = self.ref_coll_batch
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': self.batch_payment_id.bank_id.id,
            }

        if ctx_bank_batch:
            date = self.ref_coll_batch
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if loan_check:
            date = self.loan_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }
        if discount_all:
            date = self.batch_payment_id.date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if refund:
            date = self.refund_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if refund_delivery:
            date = self.refund_delivery_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if ctx_del_batch:
            date = self.batch_payment_id.date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if ctx_del:
            date = self.delivery_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }
        if ctx_bank:
            date = self.withdrawal_date
            return {
                'name': name,
                'date': date or self.move_date or self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        if self.move_date:
            return {
                'name': name,
                'date': self.move_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }

        else:
            return {
                'name': name,
                'date': self.payment_date,
                'ref': ref or self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }
