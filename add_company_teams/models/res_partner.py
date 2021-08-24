# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_team_id = fields.Many2one(
        'company.team', "User's company Team",
        help='Company Team the user is member of. Used to compute the members of a Company Team through the inverse one2many')