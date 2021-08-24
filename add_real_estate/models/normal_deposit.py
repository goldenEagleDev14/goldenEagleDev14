# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
import datetime
from odoo.exceptions import ValidationError


class account_batch_payment(models.Model):
    _inherit = 'account.batch.payment'

    @api.constrains('payment_ids')
    def _check_company_stock_request(self):
        for p in self.payment_ids:
            if p.is_main == True:
                raise ValidationError(
                    _("You Must\\'t Select Payment Maintenance  This Payment %s")%(p.name))