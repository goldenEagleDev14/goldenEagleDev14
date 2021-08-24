# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
import logging
_logger = logging.getLogger(__name__)
class historypropertyarea(models.Model):
    _name = 'history.property.area.price'

    name = fields.Char(string='Title', translate=True)
    date = fields.Date(string="Date Change", required=False, )
    area_price = fields.Float(string="Area Price ",  required=False,)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )

    # general
    type_of_property_id = fields.Many2one('property.type', _('Property Type'))
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'), store=True)
    state = fields.Selection([('draft', _('Draft')), ('available', _('Available')),
                               ('reserved', _('Reserved')),
                               ('blocked', _('Blocked'))], string="state", default='draft', copy=False)
    plot_area = fields.Float(string="Plot Area m²",  required=False, )
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )
    price_m_a = fields.Float(string="Area Price m²",  required=False, )
    total_garden_area = fields.Float(string="Total Garden Area m²",  required=False, )
    back_yard = fields.Float(string="Back Yard m²",  required=False, )
    front_yard = fields.Float(string="Front Yard m²",  required=False, )
    location_of_property_id = fields.Many2one('property.location', _('Property Location'))
    is_finish = fields.Boolean(string="Are you going to finish?",  )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²",  required=False, )
    design_of_property_id = fields.Many2one('property.design', _('Property Design'))
    is_pool = fields.Boolean(string="Is Pool ?",  )
    price_pool_for_one = fields.Float(string="Price Per Pool",  required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False, )
    price_profile = fields.Char(string="Pricing Profile ", required=False, )

class historypropertyunitprice(models.Model):
    _name = 'history.property.unit.price'

    name = fields.Char(string='Title', translate=True)
    date = fields.Date(string="Date Change", required=False, )
    unit_price = fields.Float(string="Unit Price ",  required=False,)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )

    # general
    type_of_property_id = fields.Many2one('property.type', _('Property Type'))
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'), store=True)
    state = fields.Selection([('draft', _('Draft')), ('available', _('Available')),
                               ('reserved', _('Reserved')),
                               ('blocked', _('Blocked'))], string="state", default='draft', copy=False)
    plot_area = fields.Float(string="Plot Area m²",  required=False, )
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )
    price_m = fields.Float(string="Price m²",  required=False, )
    total_garden_area = fields.Float(string="Total Garden Area m²",  required=False, )
    back_yard = fields.Float(string="Back Yard m²",  required=False, )
    front_yard = fields.Float(string="Front Yard m²",  required=False, )
    location_of_property_id = fields.Many2one('property.location', _('Property Location'))
    is_finish = fields.Boolean(string="Are you going to finish?",  )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²",  required=False, )
    design_of_property_id = fields.Many2one('property.design', _('Property Design'))
    is_pool = fields.Boolean(string="Is Pool ?",  )
    price_pool_for_one = fields.Float(string="Price Per Pool",  required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False, )
    price_profile = fields.Char(string="Pricing Profile ", required=False, )



class historypropertyfinishingprice(models.Model):
    _name = 'history.property.finishing.price'

    name = fields.Char(string='Title', translate=True)
    date = fields.Date(string="Date Change", required=False, )
    finishing_price = fields.Float(string="Finishing Price ",  required=False,)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )

    # general
    type_of_property_id = fields.Many2one('property.type', _('Property Type'))
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'), store=True)
    state = fields.Selection([('draft', _('Draft')), ('available', _('Available')),
                               ('reserved', _('Reserved')),
                               ('blocked', _('Blocked'))], string="state", default='draft', copy=False)
    plot_area = fields.Float(string="Plot Area m²",  required=False, )
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )
    price_m = fields.Float(string="Price m²",  required=False, )
    total_garden_area = fields.Float(string="Total Garden Area m²",  required=False, )
    back_yard = fields.Float(string="Back Yard m²",  required=False, )
    front_yard = fields.Float(string="Front Yard m²",  required=False, )
    location_of_property_id = fields.Many2one('property.location', _('Property Location'))
    is_finish = fields.Boolean(string="Are you going to finish?",  )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²",  required=False, )
    design_of_property_id = fields.Many2one('property.design', _('Property Design'))
    is_pool = fields.Boolean(string="Is Pool ?",  )
    price_pool_for_one = fields.Float(string="Price Per Pool",  required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False, )
    price_profile = fields.Char(string="Pricing Profile ", required=False, )


class historypropertypoolprice(models.Model):
    _name = 'history.property.pool.price'

    name = fields.Char(string='Title', translate=True)
    date = fields.Date(string="Date Change", required=False, )
    pool_price = fields.Float(string="Pool Price ",  required=False,)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )

    # general
    type_of_property_id = fields.Many2one('property.type', _('Property Type'))
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'), store=True)
    state = fields.Selection([('draft', _('Draft')), ('available', _('Available')),
                               ('reserved', _('Reserved')),
                               ('blocked', _('Blocked'))], string="state", default='draft', copy=False)
    plot_area = fields.Float(string="Plot Area m²",  required=False, )
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )
    price_m = fields.Float(string="Price m²",  required=False, )
    total_garden_area = fields.Float(string="Total Garden Area m²",  required=False, )
    back_yard = fields.Float(string="Back Yard m²",  required=False, )
    front_yard = fields.Float(string="Front Yard m²",  required=False, )
    location_of_property_id = fields.Many2one('property.location', _('Property Location'))
    is_finish = fields.Boolean(string="Are you going to finish?",  )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²",  required=False, )
    design_of_property_id = fields.Many2one('property.design', _('Property Design'))
    is_pool = fields.Boolean(string="Is Pool ?",  )
    price_pool_for_one = fields.Float(string="Price Per Pool",  required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False, )
    price_profile = fields.Char(string="Pricing Profile ", required=False, )

class historypropertygardenprice(models.Model):
    _name = 'history.property.garden.price'

    name = fields.Char(string='Title', translate=True)
    date = fields.Date(string="Date Change", required=False, )
    garden_price = fields.Float(string="Garden Price ",  required=False,)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )

    # general
    type_of_property_id = fields.Many2one('property.type', _('Property Type'))
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'), store=True)
    state = fields.Selection([('draft', _('Draft')), ('available', _('Available')),
                               ('reserved', _('Reserved')),
                               ('blocked', _('Blocked'))], string="state", default='draft', copy=False)
    plot_area = fields.Float(string="Plot Area m²",  required=False, )
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )
    price_m = fields.Float(string="Price m²",  required=False, )
    total_garden_area = fields.Float(string="Total Garden Area m²",  required=False, )
    back_yard = fields.Float(string="Back Yard m²",  required=False, )
    front_yard = fields.Float(string="Front Yard m²",  required=False, )
    location_of_property_id = fields.Many2one('property.location', _('Property Location'))
    is_finish = fields.Boolean(string="Are you going to finish?",  )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²",  required=False, )
    design_of_property_id = fields.Many2one('property.design', _('Property Design'))
    is_pool = fields.Boolean(string="Is Pool ?",  )
    price_pool_for_one = fields.Float(string="Price Per Pool",  required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False, )
    price_profile = fields.Char(string="Pricing Profile ", required=False, )

    is_garage = fields.Boolean(string="Is Garage ?", )
    price_garage_for_one = fields.Float(string="Price Per Garage", required=False, )
    number_of_garage = fields.Integer(string="Number Of Garage", required=False, default=1)

class historypropertygarageprice(models.Model):
    _name = 'history.property.garage.price'

    name = fields.Char(string='Title', translate=True)
    date = fields.Date(string="Date Change", required=False, )
    garage_price = fields.Float(string="Garage Price ",  required=False,)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )

    # general
    type_of_property_id = fields.Many2one('property.type', _('Property Type'))
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'), store=True)
    state = fields.Selection([('draft', _('Draft')), ('available', _('Available')),
                               ('reserved', _('Reserved')),
                               ('blocked', _('Blocked'))], string="state", default='draft', copy=False)
    plot_area = fields.Float(string="Plot Area m²",  required=False, )
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )
    price_m = fields.Float(string="Price m²",  required=False, )
    total_garden_area = fields.Float(string="Total Garden Area m²",  required=False, )
    back_yard = fields.Float(string="Back Yard m²",  required=False, )
    front_yard = fields.Float(string="Front Yard m²",  required=False, )
    location_of_property_id = fields.Many2one('property.location', _('Property Location'))
    is_finish = fields.Boolean(string="Are you going to finish?",  )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²",  required=False, )
    design_of_property_id = fields.Many2one('property.design', _('Property Design'))
    is_pool = fields.Boolean(string="Is Pool ?",  )
    price_pool_for_one = fields.Float(string="Price Per Pool",  required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False, )
    price_profile = fields.Char(string="Pricing Profile ", required=False, )

    is_garage = fields.Boolean(string="Is Garage ?", )
    price_garage_for_one = fields.Float(string="Price Per Garage", required=False, )
    number_of_garage = fields.Integer(string="Number Of Garage", required=False, default=1)