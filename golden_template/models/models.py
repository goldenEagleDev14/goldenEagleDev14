# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'project.project'

    pro_logo = fields.Binary(string="Image",)
