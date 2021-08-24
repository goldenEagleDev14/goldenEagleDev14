from openerp import models, fields, api, _
import datetime
from openerp.exceptions import ValidationError



class RejectedCheck(models.Model):
    _name = 'rejected.check'
    _rec_name = 'rejection_action'

    rejection_action = fields.Selection([('transfer', _('Transfer To')),
                                         ('receive', _('Manual Payment'))], 'Rejection Action')
    payment_strg_id = fields.Many2one('payment.strg', string='Payment')
    penalty_journal_entry_id = fields.Many2one('account.move', _('Penalty Fees Journal Entry'))

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', related='payment_strg_id.sale_order_id')
    customer_id = fields.Many2one('res.partner', string='customer', related='payment_strg_id.reserve_id.customer_id')
    journal_id = fields.Many2one('account.journal', _('Journal'))
    rejected = fields.Boolean('Rejected')

    penalty_date = fields.Date(_('Deduction Payment Date'))
    penalty_journal_id = fields.Many2one('account.journal', _('Deduction Journal'))
    deduction_amount = fields.Float(_('Deduction Amount'))
    apply_penalty = fields.Boolean(string='Apply Penalty')
    days_diff = fields.Integer( string='Days Diff', related='payment_strg_id.days_diff')

    # @api.multi
    def ignore(self):
        for rec in self:
            rec.apply_penalty = False if rec.days_diff < 0 else None
            rec.button_rejected_check()

    # @api.multi
    def button_rejected_check(self):
        vals = {}
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        payment_obj = self.env['account.payment']

        for rec in self:
            rejection_journal_id = self.env['ir.values'].get_default('sky.height.settings', 'reject_journal_id')
            if not rejection_journal_id:
                raise ValidationError(_("Please set rejection journal from configuration."))
            rejection_journal_obj = self.env['account.journal'].browse(rejection_journal_id)
            under_collection_journal_id = self.env['ir.values'].get_default('sky.height.settings',
                                                                            'under_collection_journal_id')
            if not under_collection_journal_id:
                raise ValidationError(_("Please set under collection journal from skyheights configuration."))
            under_collection_journal_obj = self.env['account.journal'].browse(under_collection_journal_id)
            # create 1st entry
            if rec.rejection_action == 'transfer':
                rejection_move_obj = move_obj.create(
                    {'date': datetime.date.today(), 'journal_id': rejection_journal_obj.id})
                move_line_obj.with_context(check_move_validity=False).create({
                    'move_id': rejection_move_obj.id,
                    'date': datetime.date.today(),
                    'date_maturity': rec.payment_strg_id.payment_date,
                    'journal_id': rejection_journal_obj.id,
                    'account_id': rejection_journal_obj.default_credit_account_id.id,
                    'partner_id': rec.customer_id.id,
                    'project_id': rec.payment_strg_id.project_id.id,
                    'name': 'Reject Payment in Receive Checks',
                    'debit': rec.payment_strg_id.amount,
                    'credit': 0.0,
                    'amount_currency': 0.0})

                move_line_obj.with_context(check_move_validity=False).create({
                    'move_id': rejection_move_obj.id,
                    'date': datetime.date.today(),
                    'date_maturity': rec.payment_strg_id.payment_date,
                    'journal_id': rejection_journal_obj.id,
                    'account_id': under_collection_journal_obj.default_credit_account_id.id,
                    'partner_id': rec.customer_id.id,
                    'name': 'Reject Payment in Receive Checks',
                    'credit': rec.payment_strg_id.amount,
                    'debit': 0.0,
                    'amount_currency': 0.0})
                rejection_move_obj.post()
                second_rejection_move_obj = move_obj.create(
                    {'date': datetime.date.today(), 'journal_id': rejection_journal_obj.id})
                # create 2nd entry if transfer

                move_line_obj.with_context(check_move_validity=False).create({
                    'move_id': second_rejection_move_obj.id,
                    'date': datetime.date.today(),
                    'date_maturity': rec.payment_strg_id.payment_date,
                    'journal_id': rejection_journal_obj.id,
                    'account_id': rec.journal_id.default_credit_account_id.id,
                    'partner_id': rec.customer_id.id,
                    'project_id': rec.payment_strg_id.project_id.id,
                    'name': 'Reject Payment in Receive Checks',
                    'debit': rec.payment_strg_id.amount,
                    'credit': 0.0,
                    'amount_currency': 0.0})

                move_line_obj.with_context(check_move_validity=False).create({
                    'move_id': second_rejection_move_obj.id,
                    'date': datetime.date.today(),
                    'date_maturity': rec.payment_strg_id.payment_date,
                    'journal_id': rejection_journal_obj.id,
                    'account_id': rejection_journal_obj.default_credit_account_id.id,
                    'partner_id': rec.customer_id.id,
                    'name': 'Reject Payment in Receive Checks',
                    'credit': rec.payment_strg_id.amount,
                    'debit': 0.0,
                    'amount_currency': 0.0})
            if rec.days_diff < 0 and rec.apply_penalty:
                    if not rec.penalty_journal_id:
                        raise ValidationError(_('Please Select Deduction Journal'))
                    if not rec.penalty_date:
                        raise ValidationError(_('Please Select Deduction Payment Date'))

                    # create penalty entry
                    penalty_move_obj = move_obj.create({'date': datetime.date.today(),
                                                                'journal_id': rec.penalty_journal_id.id})
                    # create debit line for payment
                    penalty_revenue_account_id = self.env['ir.values'].get_default('sky.height.settings',
                                                                                   'penalty_revenue_account_id')
                    if not penalty_revenue_account_id:
                        raise ValidationError(_("Please configure penalty account from setting!!"))
                    penalty_revenue_account_obj = self.env['account.account'].browse(penalty_revenue_account_id)
                    move_line_obj.with_context(check_move_validity=False).create({
                        'move_id': penalty_move_obj.id,
                        'date': datetime.date.today(),
                        'date_maturity': rec.payment_strg_id.payment_date,
                        'journal_id': rec.penalty_journal_id.id,
                        'account_id': rec.penalty_journal_id.default_debit_account_id.id,
                        'partner_id': rec.payment_strg_id.partner_id.id,
                        'name': rec.payment_strg_id.description,
                        'debit': rec.deduction_amount,
                        'credit': 0.0,
                        'amount_currency': 0.0})

                    # create credit line for payment
                    move_line_obj.with_context(check_move_validity=False).create({
                        'move_id': penalty_move_obj.id,
                        'date': datetime.date.today(),
                        'date_maturity': rec.payment_strg_id.payment_date,
                        'journal_id': rec.penalty_journal_id.id,
                        'account_id': penalty_revenue_account_obj.id,
                        'partner_id': rec.payment_strg_id.partner_id.id,
                        'name': rec.payment_strg_id.description,
                        'credit': rec.deduction_amount,
                        'debit': 0.0,
                        'amount_currency': 0.0})

                    penalty_move_obj.journal_id = rec.penalty_journal_id.id
                    penalty_move_obj.post()
                    rec.write({'penalty_journal_entry_id': penalty_move_obj.id})
            # if rec.rejection_action == 'receive':
            #     # create 2nd entry if receive
            #     move_line_obj.with_context(check_move_validity=False).create({
            #         'move_id': second_rejection_move_obj.id,
            #         'date': datetime.date.today(),
            #         'date_maturity': rec.payment_strg_id.payment_date,
            #         'journal_id': rejection_journal_obj.id,
            #         'account_id': under_collection_journal_obj.default_credit_account_id.id,
            #         'partner_id': rec.customer_id.id,
            #         'project_id': rec.payment_strg_id.project_id.id,
            #         'name': 'Reject Payment in Receive Checks',
            #         'debit': rec.payment_strg_id.amount,
            #         'credit': 0.0,
            #         'amount_currency': 0.0})
            #
            #     move_line_obj.with_context(check_move_validity=False).create({
            #         'move_id': second_rejection_move_obj.id,
            #         'date': datetime.date.today(),
            #         'date_maturity': rec.payment_strg_id.payment_date,
            #         'journal_id': rejection_journal_obj.id,
            #         'account_id': rejection_journal_obj.default_credit_account_id.id,
            #         'partner_id': rec.customer_id.id,
            #         'name': 'Reject Payment in Receive Checks',
            #         'credit': rec.payment_strg_id.amount,
            #         'debit': 0.0,
            #         'amount_currency': 0.0})
            #     second_rejection_move_obj.post()
            # second_rejection_move_obj.post()
            rec.payment_strg_id.write({'rejection_action': 'reject'})
            rec.payment_strg_id.write({'rejected': True,'cheque_status': 'rejected'})
