from odoo import api, fields, models
from odoo.exceptions import except_orm, Warning, RedirectWarning, ValidationError


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    multi_cheque_book = fields.Boolean()
    notes_payable = fields.Many2one('account.account')
    deliver_account = fields.Many2one('account.account')
    cheque_books_ids = fields.One2many(comodel_name='cheque.books', inverse_name='account_journal_cheque_id', copy=True)
    book_prefix = fields.Char()
    reveivable_under_collection = fields.Many2one('account.account')
    discount_check_account = fields.Many2one('account.account')
    loan_account = fields.Many2one('account.account', related='bank_id.account_id', readonly=1)
    is_notes_receivable = fields.Boolean()

    #@api.one
    @api.depends('check_manual_sequencing')
    def _get_check_next_number(self):
        if self.check_sequence_id:
            self.check_next_number = self.check_sequence_id.number_next_actual

        if not self.multi_cheque_book and self.cheque_books_ids:
            cheque_book_object = [r for r in self.cheque_books_ids if r.activate == True]
            if cheque_book_object:
                cheque_book_object = cheque_book_object[0]
                if cheque_book_object.last_use == 0:
                    self.update({'check_next_number': cheque_book_object.start_from})

                else:
                    self.update({'check_next_number': cheque_book_object.last_use + 1})

        else:
            self.check_next_number = 1

    #@api.one
    def _set_check_next_number(self):
        # if self.check_next_number < self.check_sequence_id.number_next_actual:
        # raise ValidationError(_("The last check number was %s. In order to avoid a check being rejected "
        #     "by the bank, you can only use a greater number.") % self.check_sequence_id.number_next_actual)
        # if self.check_sequence_id:
        #     self.check_sequence_id.sudo().number_next_actual = self.check_next_number
        pass

    @api.onchange('multi_cheque_book')
    def rest_all_active_cheque_book(self):

        """""
            reset all cheque books line to non activated state make the bank accountant's free to use any of them in payments
            will run after multi cheque mood activate
            
        """

        if self.multi_cheque_book:
            for r in self.cheque_books_ids:
                r.active = False

    @api.constrains('cheque_books_ids')
    def one_activated_cheque_book(self):

        """""
            use it for validation
                1 - ['don't run more than one cheque book in single cheque mood']
                2 - ['can't create cheque with non realistic start and end numbers']
                3 - ['once user's run a cheque book in single mood can't run  ']
        """

        cheque_book_object = self.env['cheque.books'].search(
            [('account_journal_cheque_id', '=', self.id), ('activate', '=', True)])
        if not self.multi_cheque_book:
            if len(cheque_book_object) > 1:

                raise Warning("you can't activate more than one cheque book since you work with single cheque mood")
            else:
                if cheque_book_object.last_use > cheque_book_object.start_from:
                    cheque_book_object.read_only_data = True
                    # self.cheque_manual_sequencing = True

        cheque_books_object = self.env['cheque.books'].search([('account_journal_cheque_id', '=', self.id)])

        if cheque_books_object:
            for r in cheque_books_object:

                if r.start_from > r.end_in:
                    raise Warning("Cheque Book Can't End Before Start , check cheque book number {}!".format(r.name))

    def validate_cheque_book(self):
        cheque_book_object = self.env['cheque.books'].search(
            [('account_journal_cheque_id', '=', self.id), ('activate', '=', True)])
        if cheque_book_object.last_use + 1 > cheque_book_object.end_in:
            raise Warning("{} is ending please open new one !".format(cheque_book_object.name))

    #@api.multi
    def write(self, vals):
        if not self.multi_cheque_book:
            data = [r for r in self.cheque_books_ids if r.activate == True]

            # if 'cheque_books_ids' in vals:

            # if "activate" in vals['cheque_books_ids'][0][2]:
            #     if not vals['cheque_books_ids'][0][2]['activate']:
            #         if not data:
            #             raise Warning("please activate one check book or select multi check book options")
            #     return super(AccountJournalInherit, self).write(vals)
        if 'multi_cheque_book' in vals:
            if vals['multi_cheque_book']:
                data = [r for r in self.cheque_books_ids if r.activate == True]
                if data:
                    data = data[0]
                    if data.last_use > data.start_from and data.last_use != data.end_in or data.activate:
                        raise Warning(
                            'we have one cheque book activated in a single mood ,\nyou can\'t run another mood before you end this cheque book or deactivate it')

        if 'book_prefix' in vals:
            data =[]
            if data:
                data = data[0]
                data = [r for r in self.cheque_books_ids if r.activate == True][0]
                if data.last_use > data.start_from and data.last_use != data.end_in:
                    raise Warning('you can\'t change the prefix since it was already used')

        return super(AccountJournalInherit, self).write(vals)
