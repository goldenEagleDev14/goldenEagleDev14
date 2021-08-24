# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUser(models.Model):
    _inherit = 'res.users'


    name_Branch = fields.Char(string="Name Branch", required=False, )