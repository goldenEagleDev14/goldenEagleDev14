from odoo import models, fields, api,_


class add_reservation_unit_changes(models.Model):
    _inherit = 'res.reservation'

    property_area = fields.Float(related='property_id.sellable',string='Sellable BUA m²')
    property_garage = fields.Boolean(related='property_id.is_garage',string='Is Garage')
class add_reservation_unit_changess(models.Model):
    _inherit = 'product.product'

    net_sellable_bua = fields.Float(string='Net Sellable BUA',compute='calc_net_sellable_bua',store=True)
    load_percentage = fields.Float(string='نسبه التحميل%')

    @api.depends('load_percentage','sellable')
    def calc_net_sellable_bua(self):
        for rec in self:
            rec.net_sellable_bua = (rec.load_percentage/100) * rec.sellable
