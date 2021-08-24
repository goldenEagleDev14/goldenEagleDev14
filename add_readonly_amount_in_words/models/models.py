# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class add_readonly_amount_in_words(models.Model):
#     _name = 'add_readonly_amount_in_words.add_readonly_amount_in_words'
#     _description = 'add_readonly_amount_in_words.add_readonly_amount_in_words'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
