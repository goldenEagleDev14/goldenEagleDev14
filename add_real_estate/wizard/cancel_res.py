# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import datetime
from datetime import datetime, date,timedelta

class CancelSaleOrderPipe(models.TransientModel):
    _name = 'cancel.res'



    # reason = fields.Text(string="Reason", required=True, )
    reason = fields.Many2one(comodel_name="cancel.reason.res", string="Reason", required=True, )


    # @api.multi
    def action_apply(self):
        self.ensure_one()
        res = self.env['res.reservation'].browse(self._context.get('active_ids', []))
        res.reason = self.reason.id
        res.state = 'blocked'
        res.date_cancel_unit = datetime.now()