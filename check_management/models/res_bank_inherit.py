from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError



class BankInherit(models.Model):

    _inherit = 'res.bank'



    available_pool = fields.Float()
    central_percentage = fields.Float()
    loan_percentage = fields.Float()
    account_id =fields.Many2one('account.account')
    min_num_of_days = fields.Integer()
    max_num_of_days = fields.Integer()
    is_warning = fields.Boolean()




    @api.constrains('central_percentage','loan_percentage')
    def available_presentage_restriction(self):
        msg = ""
        if self.central_percentage > 100 or self.central_percentage < 0:
            msg+='Central percentage must be a percentage number\n'


        if self.loan_percentage > 100 or self.loan_percentage < 0:
            msg+= 'Loan percentage must be a percentage number'

        if len(msg) > 7:
            raise ValidationError(msg)
