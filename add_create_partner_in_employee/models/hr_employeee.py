# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def create_partner_new(self):
        for rec in self:
            print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGhG")
            if rec.address_home_id.id == False:
                if self.env.user.has_group('add_create_partner_in_employee.group_create_partner_employee'):
                    rec.address_home_id = self.env['res.partner'].sudo().create({'name': rec.name,
                                                                   'email': rec.work_email,
                                                                   'company_id': rec.company_id.id,
                                                                   'company_type': 'person',
                                                                   'ref':rec.zk_emp_id,
                                                                   'phone':rec.work_phone,
                                                                                 })



