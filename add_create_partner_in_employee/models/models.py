# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class add_create_partner_in_employee(models.Model):
#     _name = 'add_create_partner_in_employee.add_create_partner_in_employee'
#     _description = 'add_create_partner_in_employee.add_create_partner_in_employee'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
