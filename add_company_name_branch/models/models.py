# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class add_company_name_branch(models.Model):
#     _name = 'add_company_name_branch.add_company_name_branch'
#     _description = 'add_company_name_branch.add_company_name_branch'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
