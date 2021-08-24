# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class sale_configuration(models.TransientModel):
    _inherit = 'res.config.settings'

    lead_period = fields.Integer('Lead Expiration Period')
    lead_period_compute = fields.Integer(string="",compute="_compute_lead_period" )

    @api.depends("lead_period")
    def _compute_lead_period(self):
        for rec in self:
            _logger.info("here  :: ")
            test = self.env['res.config.settings'].search([])
            vaule = 0
            for t in test:
                vaule = t.lead_period
                _logger.info("vaule  :: %s", vaule)
            rec.lead_period_compute = vaule

    @api.model
    def get_default_sale_config(self, fields):
        lead_period = self.env['ir.values'].get_default('sale.config.settings', 'lead_period_new')
        return {
            'lead_period': lead_period,
        }

    # @api.multi
    def set_sale_defaults(self):
        self.ensure_one()
        for rec in self:
            if rec.lead_period < 0:
                raise ValidationError("Sorry... Lead Expiration Period must be positive !!!")
            lead_period = rec.lead_period
            res = self.env['ir.values'].sudo().set_default('sale.config.settings', 'lead_period', lead_period)
            return res