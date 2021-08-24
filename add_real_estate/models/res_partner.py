# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_broker = fields.Boolean(_('Broker'))
    organization = fields.Char(_('Organization'))
    nationality = fields.Char(string="Nationality", required=False, )
    id_def = fields.Char(string="ID", required=False, )
    social_status = fields.Selection(string="Social Status", selection=[('married', 'Married'), ('single', 'Single'), ], required=False, )
    # company_team_id = fields.Many2one(
    #     'company.team', "User's company Team",
    #     help='Company Team the user is member of. Used to compute the members of a Company Team through the inverse one2many')