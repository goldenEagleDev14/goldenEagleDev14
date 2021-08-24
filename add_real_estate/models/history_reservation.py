# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
import logging
_logger = logging.getLogger(__name__)
class historyReservation(models.Model):
    _name = 'history.reservation'

    name = fields.Char(string='Title', translate=True)
    date = fields.Date(string="Date Change", required=False, )
    state = fields.Selection(string="State", selection=[('draft', 'Draft'),('reserved', 'Reserved'),('contracted', 'Contracted'), ('blocked', 'Blocked'), ], required=False ,default='draft')
    res_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=False, )
    unit_id = fields.Many2one(comodel_name="product.product", string="Unit", required=False, )