# -*- coding: utf-8 -*-


from odoo import models, fields, api


class MarketPlanning(models.Model):
    _name='market.plan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    # _inherit = ['mail.thread.cc', 'mail.thread.blacklist', 'mail.activity.mixin',
    #             'utm.mixin', 'format.address.mixin', 'phone.validation.mixin']
    name = fields.Char(string="", required=False, )
    platform_id = fields.Many2one(comodel_name="platform.plan", string="Platform", required=False, )
    category_id = fields.Many2one(comodel_name="category.plan", string="Category", required=False, )
    type_id = fields.Many2one(comodel_name="type.plan", string="Type", required=False, )
    target_id = fields.Many2one(comodel_name="target.plan", string="Target", required=False, )
    ads_name = fields.Text(string="Ads Name", required=False, )
    ads_link = fields.Char(string="Ads Link", required=False, )
    ads_marketing_cost = fields.Float(string="Ads Marketing Cost",  required=False, )
    lead_cost = fields.Float(string="Lead Cost",  required=False,compute="_compute_lead_cost" )
    planned_leads = fields.Float(string="Planned Leads",  required=False, )
    actual_leads = fields.Float(string="Actual Leads",  required=False, )
    start_palnned_date = fields.Date(string="Start Planned Date", required=False, )
    end_palnned_date = fields.Date(string="End Planned Date", required=False, )
    start_actual_date = fields.Date(string="Start Actual Date", required=False, )
    end_actual_date = fields.Date(string="End Actual Date", required=False, )
    owner_id = fields.Many2one(comodel_name="hr.employee", string="Owner", required=False,domain="[('is_project_owner', '=',True)]" )
    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=False, )
    lead_type_id = fields.Many2one(comodel_name="lead.type.plan", string="Lead Type", required=False, )

    # planned_week = fields.Integer(string="Planned Week", required=False,compute="_compute_week" )
    # actual_week = fields.Integer(string="Actual Week", required=False,compute="_compute_week" )
    # def _compute_week(self):
    #     for rec in self:
    #         rec.planned_week = 0
    #         rec.actual_week = 0

    def _compute_lead_cost(self):
        for rec in self:
            if rec.actual_lead_count > 0 :
                rec.lead_cost = rec.ads_marketing_cost / rec.actual_lead_count
            else:
                rec.lead_cost = 0.0

    def action_lead_view(self):

        self.ensure_one()
        action = self.env.ref('crm.crm_lead_action_pipeline').read()[0]

        action['domain'] = [
            # ('state', 'in', ['posted', 'paid']),
            ('market_plan_id', '=', self.id),
            ('type', '=', 'opportunity')
        ]
        return action
    def action_lead_visit_view(self):
        self.ensure_one()
        action = self.env.ref('crm.crm_lead_action_pipeline').read()[0]
        action['domain'] = [
            # ('state', 'in', ['posted', 'paid']),
            ('market_plan_id', '=', self.id),
            ('type', '=', 'opportunity'),
            ('is_visit', '=', True),
        ]
        return action
    actual_lead_count = fields.Integer('# Actual Lead', compute='_compute_actual_lead_count')
    visit_lead_count = fields.Integer('# Visit', compute='_compute_actual_lead_count')

    def _compute_actual_lead_count(self):

        for rec in self:
            leads = self.env['crm.lead'].search([('market_plan_id', '=', rec.id), ('type', '=', 'opportunity')])
            total_meeting = 0
            rec.actual_lead_count = len(leads)
            for lead in  leads:
                if lead.is_visit == True:
                    total_meeting +=1

            rec.visit_lead_count = total_meeting
    date = fields.Date(string='date', default=fields.Date.context_today, required=True)

    @api.model
    def create(self, vals):
        # res = super(res_partner_inherit, self).create(vals)
        sequence_code = 'marketing.plan.code.sequence'
        code = str(self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=self.date))
        vals['name'] = code
        return super(MarketPlanning, self).create(vals)

class PlatformModel(models.Model):
    _name='platform.plan'

    name = fields.Char(string=" Name ", required=True, )

class CategoryModel(models.Model):
    _name='category.plan'

    name = fields.Char(string=" Name ", required=True, )


class TypeModel(models.Model):
    _name='type.plan'

    name = fields.Char(string=" Name ", required=True, )


class TargetModel(models.Model):
    _name='target.plan'

    name = fields.Char(string=" Name ", required=True, )


class LeadTypeModel(models.Model):
    _name='lead.type.plan'

    name = fields.Char(string=" Name ", required=True, )

