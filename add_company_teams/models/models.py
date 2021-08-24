# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class add_company_teams(models.Model):
#     _name = 'add_company_teams.add_company_teams'
#     _description = 'add_company_teams.add_company_teams'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
