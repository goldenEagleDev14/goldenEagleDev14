# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import date
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class PropertyCategory(models.Model):
    _name = "property.exception"
    _description = "Property Exception"

    name = fields.Text('Name', required=True, translate=True)


class PropertyCategory(models.Model):
    _name = "property.category"
    _description = "Property Category"

    name = fields.Char('Name', required=True, translate=True)

class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property Types"

    name = fields.Char('Name', required=True, translate=True)
    cate_id = fields.Many2one(comodel_name="property.category", string="Category", required=True, )
    multi_image = fields.Boolean(string="Add  Multiple Images?")
    images_type = fields.One2many('biztech.product.images', 'type_id',
                              string='Images')
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )

class PropertyLocation(models.Model):
    _name = "property.location"
    _description = "Property Locations"

    name = fields.Char('Property location', required=True, translate=True)


class PropertyLocation(models.Model):
    _name = "property.finished.type"
    _description = "Property Finishing Type"

    name = fields.Char('Finishing Type', required=True, translate=True)


class PropertyDesign(models.Model):
    _name = "property.design"
    _description = "Property Design"

    name = fields.Char('Property Design', required=True, translate=True)



class latlng_line(models.Model):
    _name = "latlng.line"
    lat= fields.Float('Latitude', digits=(9, 6),required=True)
    lng= fields.Float('Longitude', digits=(9, 6),required=True)
    url= fields.Char('URL', digits=(9, 6),required=True)
    city_id= fields.Many2one('res.country.state', 'City')
    unit_id= fields.Many2one('product.product', 'Unit')


class CancelReason(models.Model):
    _name = "cancel.reason.res"

    name = fields.Char('Reason', required=True, translate=True)