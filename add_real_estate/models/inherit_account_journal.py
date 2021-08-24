from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    show_checks = fields.Boolean(string='Show Checks')
    under_collected_account_id = fields.Many2one('account.account',string="Under Collection Account")
    collection_account_id = fields.Many2one('account.account', string="Collection Account")
