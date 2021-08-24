from odoo import models, fields, api


class Level(models.Model):
    _name = 'property.level'
    _description = 'property level'

    name = fields.Char('Level', required=True)
    _sql_constraints = [
        ('property_level_unique_constraint', 'UNIQUE(name)', 'This level record already exists')
    ]


class Product(models.Model):
    _inherit = 'product.product'

    property_level = fields.Many2one('property.level')
