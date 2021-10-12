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
    is_duplex = fields.Boolean(string='Is Duplex')
    first_floor_area = fields.Float(string='First Floor Area')
    first_floor_prices = fields.Float(string='First Floor Prices')
    total_first = fields.Float(compute='calc_total_first')
    ground_floor_area = fields.Float(string='First Ground Area')
    ground_floor_prices = fields.Float(string='First Ground Prices',store=True)
    total_ground = fields.Float(compute='calc_total_ground',store=True)
    @api.depends('first_floor_area','first_floor_prices')
    def calc_total_first(self):
        for r in self:
            r.total_first = r.first_floor_area * r.first_floor_prices
    @api.depends('ground_floor_area','ground_floor_prices')
    def calc_total_ground(self):
        for r in self:
            r.total_ground = r.ground_floor_area * r.ground_floor_prices


    def _compute_unit_price(self):
        for rec in self:
            if rec.is_duplex:
                rec.unit_price = rec.total_ground + rec.total_first
            elif rec.price_m > 0 :
                rec.unit_price = rec.price_m * rec.sellable
                if rec.unit_price != rec.unit_price2:
                    rec.update({
                        'unit_price2': rec.unit_price
                    })
                    rec.unit_price2 == rec.unit_price
            else:
                rec.unit_price = 0


