from odoo import models, fields, api


class PaymentDetails(models.Model):
    _inherit = 'rs.payment_strategy_details'

    is_installment = fields.Boolean(default=False)
