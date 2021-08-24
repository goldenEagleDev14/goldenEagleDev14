from openerp import models, fields, api, _


class SelectClerk(models.Model):
    _name = 'select.clerk'

    def _get_default_fees(self):
        return self.env['ir.values'].get_default('sky.height.settings', 'penalty_percentage')


    penalty_date = fields.Date('Deduction Payment Date')
    penalty_journal_id = fields.Many2one('account.journal', 'Deduction Journal')
    penalty_fees = fields.Float('Penalty Fees', default=_get_default_fees)
    apply_penalty = fields.Boolean()

    # @api.multi
    def set_penalty(self):
        for rec in self:
            if self.env.context.get('default_payment_strg_ids', []):
                for py in self.env.context.get('default_payment_strg_ids', []):
                    payment = self.env['payment.strg'].browse(py)
                    if payment.cheque_status == 'under_collection':
                        if payment.days_diff < 0:
                            total_amount = payment.amount
                            for day in range(-1 * payment.days_diff):
                                total_amount = total_amount + ((self.penalty_fees * total_amount) / 100)

                            payment.deduction_amount = total_amount - payment.amount
                            payment.apply_penalty = True
                            payment.penalty_date = rec.penalty_date
                            payment.penalty_journal_id = rec.penalty_journal_id.id
                        payment.apply()
            elif self.env.context.get('active_ids', []):
                for py in self.env.context.get('active_ids', []):
                    payment = self.env['payment.strg'].browse(py)
                    if payment.cheque_status == 'under_collection':
                        if payment.days_diff < 0:
                            payment.deduction_amount = (self.penalty_fees * payment.amount) / 100
                            payment.apply_penalty = True
                            payment.penalty_date = rec.penalty_date
                            payment.penalty_journal_id = rec.penalty_journal_id.id
                        payment.apply()

    # @api.multi
    def ignore_penalty(self):
        for rec in self:
            if self.env.context.get('default_payment_strg_ids', []):
                for py in self.env.context.get('default_payment_strg_ids', []):
                    payment = self.env['payment.strg'].browse(py)
                    if payment.cheque_status == 'under_collection':
                        payment.apply_penalty = False
                        payment.ignore()
            elif self.env.context.get('active_ids', []):
                for py in self.env.context.get('active_ids', []):
                    payment = self.env['payment.strg'].browse(py)
                    if payment.cheque_status == 'under_collection':
                        payment.apply_penalty = False
                        payment.ignore()
