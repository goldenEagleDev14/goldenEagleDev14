from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ChequeBook(models.Model):
    _name = 'cheque.books'
    _rec_name = 'name'

    name = fields.Char(compute='get_name', store=True, string='Number')
    start_from = fields.Integer()
    end_in = fields.Integer()
    last_use = fields.Integer()
    activate = fields.Boolean()
    account_journal_cheque_id = fields.Many2one('account.journal')
    read_only_data = fields.Boolean()
    used_book = fields.Boolean(string='Used',compute='get_used_book')
    book_state = fields.Selection([('draft', 'draft'), ('open', 'Open'), ('done', 'Done')], default='draft')

    #@api.multi
    def get_used_book(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>55")
        for rec in self:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>66")
            if rec.book_state in ['open','done']:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>33")
                rec.used_book = True
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>44")
            else:
                rec.used_book = False
    @api.depends('start_from', 'end_in')
    def get_name(self):
        for r in self:
            if r.account_journal_cheque_id.book_prefix:
                name = r.account_journal_cheque_id.book_prefix
            else:
                name = 'Pref'
            r.name = name + '/' + str(r.start_from) + '/' + str(r.end_in)

    def delete_line(self):
        if self.book_state != 'draft':
            raise ValidationError("you can't remove a opening or done check book")
        self.unlink()
        return super(ChequeBook, self).unlink()

    #@api.multi
    def write(self, valus):
        base_journal = self.account_journal_cheque_id.id
        pay_book_obj = self.env['cheque.books'].search([('account_journal_cheque_id', '=', base_journal)])
        if 'start_from' in valus:
            start = valus['start_from']
            if self.last_use > 0 and self.last_use != self.end_in:
                raise ValidationError('this check is opened can\'t change any field')

        else:
            start = self.start_from

        if 'end_in' in valus:
            end = valus['end_in']
            if self.last_use > 0:
                raise ValidationError('this check is opened can\'t change any field')
        else:
            end = self.end_in
        if 'last_use' in valus:
            if valus['last_use'] == end:
                self.book_state = 'done'
            else:
                self.book_state = 'open'
        # if 'activate' in valus:
        #     if self.account_journal_cheque_id.multi_cheque_book:
        #         raise ValidationError(
        #             "you can't work with single check book mood since you are already in multi check book mood")
        if (
                self.last_use > 0 and self.last_use != self.end_in) and 'activate' in valus and not self.account_journal_cheque_id.multi_cheque_book:
            raise ValidationError('this check is opened can\'t change any field')

        if end < start:
            raise ValidationError("you can't start after end")
        list_start = [r for r in pay_book_obj if start <= r.end_in and start >= r.start_from and r.id != self.id]
        list_end = [r for r in pay_book_obj if end <= r.end_in and end >= r.start_from and r.id != self.id]

        if list_start:
            raise ValidationError(
                "your start number is not correct \nyou can't add cheque within start or end number in between {} and {}".format(
                    list_start[0].start_from, list_start[0].end_in))
        if list_end:
            raise ValidationError(
                "your end number is not correct \nyou can't add cheque within start or end number in between {} and {}".format(
                    list_end[0].start_from, list_end[0].end_in))

        return super(ChequeBook, self).write(valus)

    @api.model
    def create(self, vals):
        base_journal = vals['account_journal_cheque_id']
        pay_book_obj = self.env['cheque.books'].search([('account_journal_cheque_id', '=', base_journal)
                                                        ])
        start = vals['start_from']
        end = vals['end_in']
        if end < start:
            raise ValidationError("you can't start after end")
        list_start = [r for r in pay_book_obj if start <= r.end_in and start >= r.start_from]
        list_end = [r for r in pay_book_obj if end <= r.end_in and end >= r.start_from]

        if list_start:
            raise ValidationError(
                "your start number is not correct \nyou can't add cheque within start or end number in between {} and {}".format(
                    list_start[0].start_from, list_start[0].end_in))
        if list_end:
            raise ValidationError(
                "your end number is not correct \nyou can't add cheque within start or end number in between {} and {}".format(
                    list_end[0].start_from, list_end[0].end_in))

        # if 'activate' in vals:
        #     if vals['activate'] == True:
        #         journal_obj = self.env['account.journal'].browse(vals['account_journal_cheque_id'])
        #         if journal_obj.multi_cheque_book:
        #             raise ValidationError(
        #                 "you can't work with single check book mood since you are already in multi check book mood")

        return super(ChequeBook, self).create(vals)
