# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class projectPoject(models.Model):
    _inherit = 'project.project'

    city_id = fields.Many2one(comodel_name="res.country.state", string="City", required=False, )
    condition_terms = fields.Text(string="شروط الحجز", required=False, )
    condition_terms_broker = fields.Text(string="شروط الحجز (Broker)", required=False, )
    property_account_income_id = fields.Many2one('account.account', company_dependent=True,
        string="Income Account",
        domain="['&', ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="Keep this field empty to use the default value from the product category.")


    units_count = fields.Integer(compute='_compute_units_count', string="Units Count")
    label_units = fields.Char(string='Units', default='Units')

    units_draft_count = fields.Integer(compute='_compute_units_count', string="Units Draft Count")
    label_draft = fields.Char(string='Draft Units ', default='Draft Units ')

    units_request_count = fields.Integer(compute='_compute_units_count', string="Units Request Count")
    label_request = fields.Char(string='Request Units ', default='Request Units ')

    units_approve_count = fields.Integer(compute='_compute_units_count', string="Units Approve Count")
    label_approve = fields.Char(string='Approve Units ', default='Approve Units ')

    units_available_count = fields.Integer(compute='_compute_units_count', string="Units available Count")
    label_available = fields.Char(string='Available Units ', default='Available Units ')

    units_reserved_count = fields.Integer(compute='_compute_units_count', string="Units Reserved Count")
    label_reserved = fields.Char(string='Reserved Units ', default='Reserved Units ')

    units_contracted_count = fields.Integer(compute='_compute_units_count', string="Units Contracted Count")
    label_contracted = fields.Char(string='Contracted Units ', default='Contracted Units ')

    units_blocked_count = fields.Integer(compute='_compute_units_count', string="Units Blocked Count")
    label_blocked = fields.Char(string='Blocked Units ', default='Blocked Units ')

    units_exception_count = fields.Integer(compute='_compute_units_count', string="Units Exception Count")
    label_exception = fields.Char(string='Exception Units ', default='Exception Units ')

    def _compute_units_count(self):
        for rec in self:
            units_count = self.env['product.product'].search(
                [('project_id', '=', rec.id)])
            units_draft_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'draft')])
            units_request_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'request_available')])
            units_approve_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'approve')])
            units_available_count = self.env['product.product'].search(
                [('project_id', '=', rec.id),('state', '=', 'available')])
            units_reserved_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'reserved')])
            units_contracted_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'contracted')])
            units_blocked_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'blocked')])
            units_exception_count = self.env['product.product'].search(
                [('project_id', '=', rec.id), ('state', '=', 'exception')])
            rec.units_count = len(units_count)
            rec.units_available_count = len(units_available_count)
            rec.units_reserved_count = len(units_reserved_count)
            rec.units_contracted_count = len(units_contracted_count)
            rec.units_blocked_count = len(units_blocked_count)
            rec.units_draft_count = len(units_draft_count)
            rec.units_request_count = len(units_request_count)
            rec.units_approve_count = len(units_approve_count)
            rec.units_exception_count = len(units_exception_count)

    def action_view_units(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_all').read()[0]
        print("action %s",action)
        return action
    def action_view_units_draft(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_draft').read()[0]
        return action
    def action_view_units_request(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_request_available').read()[0]
        return action
    def action_view_units_approve(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_approve').read()[0]
        return action
    def action_view_units_available(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_available').read()[0]
        return action
    def action_view_units_reserved(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_reserved').read()[0]
        return action
    def action_view_units_contracted(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_contracted').read()[0]
        return action
    def action_view_units_blocked(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_blocked').read()[0]
        return action
    def action_view_units_exception(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.act_project_units_exception').read()[0]
        return action



class ProjectPhase(models.Model):
    _name='project.phase'

    name = fields.Char('Name',required=True)
    project_id = fields.Many2one('project.project', _('Project'),required=True)

# class project_project(models.Model):
#     _name = 'project.project'
#
#     terms_and_conditions = fields.Text(string="Terms and Conditions", required=False, )
#
