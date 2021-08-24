# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    company_team_id = fields.Many2one(
        'company.team', "User's company Team",
        help='Company Team the user is member of. Used to compute the members of a Company Team through the inverse one2many')