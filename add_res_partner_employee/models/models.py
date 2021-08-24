# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    is_employee = fields.Boolean(string="Is Employee",  )

    def seecedd_confirm_employee(self):
        """
        Execute the actions to do with Employee.
        """
        for partner in self:
            emp = self.env['hr.employee'].search([('address_home_id', '=', partner.id)], limit=1)
            if emp:
                partner.is_employee = True
            else:
                partner.is_employee = False