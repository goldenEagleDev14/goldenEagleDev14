# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    ins_reminder_days = fields.Integer(string="Reminder Before Days", related='company_id.ins_reminder_days', default=2, required="1", readonly=False)
    
    @api.onchange('ins_reminder_days')
    def _check_days(self):
        if self.ins_reminder_days <= 0:
            raise ValidationError(_("Installment Reminder Days must be greater than 0"))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
