# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    projects_ids = fields.One2many(comodel_name="project.project", inverse_name="city_id", string="", required=False, )

    test = fields.Char(string="test", required=False, )