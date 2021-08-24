# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'project.project'

    condition_request = fields.Text(string="يتم تخصيص الوحدات باسبقية الحجز",)
