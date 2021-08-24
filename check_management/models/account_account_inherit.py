from odoo import api, fields, models

class NewModule(models.Model):


    _inherit = 'account.account'

    is_batch_deposit = fields.Boolean()
