from odoo import api, fields, models , _
from odoo.exceptions import  UserError



class account_move_line(models.Model):


    _inherit = 'account.move'


    @api.constrains('line_ids', 'journal_id', 'auto_reverse', 'reverse_date')
    def _validate_move_modification(self):
        pass

class Reconcile(models.Model):


    _inherit = 'account.move.line'

    name = fields.Char()


    @api.model
    def compute_amount_fields(self, amount, src_currency, company_currency, invoice_currency=False):
        """ Helper function to compute value for fields debit/credit/amount_currency based on an amount and the currencies given in parameter"""
        amount_currency = False
        currency_id = False
        if src_currency and src_currency != company_currency:
            amount_currency = amount
            amount = src_currency.with_context(self._context).compute(amount, company_currency)
            currency_id = src_currency.id
        debit = amount > 0 and amount or 0.0
        credit = amount < 0 and -amount or 0.0
        if invoice_currency and invoice_currency != company_currency and not amount_currency:
            amount_currency = src_currency.with_context(self._context).compute(amount, invoice_currency)
            currency_id = invoice_currency.id
        return debit, credit, amount_currency, currency_id
    #@api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        # Empty self can happen if the user tries to reconcile entries which are already reconciled.
        # The calling method might have filtered out reconciled lines.
        if not self:
            return True

        ctx_discount_batch = self._context.get('discount_check')
        ctx_del = self._context.get('delivery_aml')
        ctx_bank = self._context.get('bank_aml')
        ctx_del_batch = self._context.get('delivery_aml_batch')
        ctx_bank_batch = self._context.get('bank_aml_batch')
        ctx_loan_batch = self._context.get('loan_check')
        collect_disc_batch = self._context.get('collect_disc_batch')
        loan_check = self._context.get('loan_check')
        discount_all = self._context.get('discount_all')
        refund_discount = self._context.get('refund_discount')
        if collect_disc_batch or loan_check or discount_all or refund_discount or ctx_del_batch or ctx_del or ctx_bank_batch or ctx_bank or ctx_loan_batch or ctx_discount_batch:
            return True
        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        partners = set()
        for line in self:


            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.account_id.internal_type in ('receivable', 'payable')):
                partners.add(line.partner_id.id)
            if line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))

        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries!'))

        if len(set(all_accounts)) > 1:
            raise UserError(_('Entries are not of the same account!'))

        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (all_accounts[0].name, all_accounts[0].code))
        if len(partners) > 1:
            raise UserError(_('The partner has to be the same on all lines for receivable and payable accounts!'))

        #reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        #if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
            #add writeoff line to reconcile algo and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
            return writeoff_to_reconcile
        return True
