# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, time
from datetime import datetime, timedelta,date

from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _default_check_is_sales_head(self):
        if self.env.user.has_group('real_crm_custom.sales_head_user'):
            return True
        else:
            return False

    is_sales_head = fields.Boolean(compute='_check_is_sales_head', default=_default_check_is_sales_head)

    def _check_is_sales_head(self):
        for rec in self:
            rec.is_sales_head = True if self.env.user.has_group('real_crm_custom.sales_head_user') else False

    def _check_is_salesperson(self):
        for rec in self:
            rec.is_saleperson = True if self.env.user.has_group('base.group_sale_salesman') else False

    def get_domain(self):
        users = self.env['res.users'].search([])
        domain_users = []
        for user in users:
            if user.has_group('base.group_sale_salesman') or \
                    user.has_group('base.group_sale_salesman_all_leads') or \
                    user.has_group('base.group_sale_manager') or \
                    user.has_group('real_crm_custom.sale_team_leader_group'):
                domain_users.append(user.id)
        return [('id', 'in', domain_users)]

    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user, domain=get_domain)
    name = fields.Char(string='Opportunity', required=False)
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'))
    property_id = fields.Many2one('product.product', string='Property')
    marital_status = fields.Selection([('single', _("Single")), ('married', _("Married")), ('widowed', _("Widowed")),
                                       ('divorced', _("Divorced"))], _('Marital Status'))
    no_of_kids = fields.Integer(_('No. Of Family Member'))
    organization = fields.Char(_('Organization'))
    id_no = fields.Char(string="Identification No.")
    id_type = fields.Selection([('id', _("ID")), ('passport', _("Passport"))], string="Identification Type")
    id_photo = fields.Binary("Photo ID")
    user_ids = fields.Many2many('res.users', string='Sales Persons')
    broker_id = fields.Many2one('res.partner', string=_('Broker'), domain=[('is_broker', '=', True)])
    sales_type = fields.Selection([('direct', _("Direct")), ('indirect', _("Indirect")),
                                   ('individual_broker', _("Individual Broker")),
                                   ('client_referral', _("Client Referral")),
                                   ('employee_referral', _("Employee Referral")), ('resale', _("Resale")),
                                   ('upgrade', _("Upgrade")), ('supplier_through_sales', _("Supplier Through Sales")),
                                   ('supplier_through_company', _("Supplier Through Company"))], default='direct',
                                  string='Sales Type')

    source = fields.Selection([('facebook', _("Facebook")), ('callcenter', _("Call Center")), ('website', _("Website")),
                               ('broker', _("Broker")), ('referral', _("Referral")), ('ambassador', _("Ambassador")),
                               ('other', _("Other")), ('self_generated', _("Self Generated"))],
                              default='self_generated', string='Source')

    # status = fields.Selection([('available', _('Available')), ('not_available', _('Not Available')),
    #                            ('reserved', _('Reserved')), ('contracted', _('Contracted')),
    #                            ('delivered', _('Delivered'))], string="Status", related='property_id.status')
    date_expiry = fields.Date(string="Expiry Date",store=True,readonly=True)

    mobile1_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')], string="Mobile1 Type")
    note_ids = fields.One2many('lead.notes', 'lead_id')
    # is_date = fields.Boolean(string="",compute="Compute_date_expiry_date"  )
    #
    # def Compute_date_expiry_date(self):
    #     for rec in self:
    #         rec.is_date = True
    #         last_note = self.env['mail.activity'].search([('id', 'in', self.activity_ids.ids)],  limit=1,order='id DESC')
    #         _logger.info("last_note :: %s", last_note)
    #
    #         test = self.env['res.config.settings'].search([])
    #         vaule = 0
    #         for t in test:
    #             vaule = t.lead_period
    #             _logger.info("vaule  :: %s", vaule)
    #         _logger.info("test :: %s", test)
    #         # lead_period = self.env['ir.values'].get_default('res.config.settings', 'lead_period')
    #         _logger.info("enter last note 2 :: ", vaule)
    #         date = fields.Date.from_string(self.create_date)
    #         _logger.info("last_note.date_deadline :: %s", last_note.date_deadline)
    #         if len(last_note) > 0:
    #             expiry_date = (last_note.date_deadline + relativedelta(days=vaule))
    #             _logger.info("expiry_date :: %s", expiry_date)
    #
    #             self.date_expiry = expiry_date

    # is_change_state = fields.Boolean(string="",compute="Compute_is_change_state"  )
    # is_change_lead_welcome = fields.Boolean(string=""  )

    def check_date_expiry(self):
        for rec in self:
            if rec.date_expiry != False:
                if rec.date_expiry < date.today():
                    rec.type = "lead"
    # def Compute_is_change_state(self):
    #     for rec in self:
    #         rec.is_change_state = True
    #         # date1 = datetime.strptime(str(rec.date_expiry), '%Y-%m-%d %H:%M:%S')
    #         # date2 = datetime.strptime( str(fields.Date.context_today), '%Y-%m-%d %H:%M:%S')
    #         _logger.info("rec.date_expiry :: %s",rec.date_expiry)
    #         if rec.date_expiry != False:
    #             if rec.date_expiry < date.today() and rec.is_change_lead_welcome == False:
    #                 rec.type = "lead"
    #                 # rec.is_change_lead_welcome = True
    #                 rec.date_expiry = False

    # @api.depends('activity_ids')
    # @api.onchange('activity_ids')
    # def onchange_method_activity_ids_ids(self):
    #     _logger.info("here enter activity_ids onchange")
    #     for rec in self:
    #         rec.is_date = True
    #         last_note = self.env['mail.activity'].search([('id', 'in', self.activity_ids.ids)], limit=1,
    #                                                      order='id DESC')
    #         test = self.env['res.config.settings'].search([])
    #         vaule = 0
    #         for t in test:
    #             vaule = t.lead_period
    #         _logger.info("test :: %s", test)
    #         # lead_period = self.env['ir.values'].get_default('res.config.settings', 'lead_period')
    #         _logger.info("enter last note 2 :: ", vaule)
    #         date = fields.Date.from_string(self.create_date)
    #         _logger.info("last_note.date_deadline :: %s", last_note.date_deadline)
    #
    #         expiry_date = (last_note.date_deadline + relativedelta(days=vaule))
    #         _logger.info("expiry_date :: %s", expiry_date)
    #
    #         self.date_expiry = expiry_date
    # @api.onchange('note_ids')
    # def onchange_method_note_ids(self):
    #     # last_note = self.env['lead.notes'].search([('lead_id', '=', self.activity_ids)],  limit=1,order='id DESC')
    #     last_note = self.env['lead.notes'].search([('lead_id', '=', self.id)],  limit=1,order='id DESC')
    #     test = self.env['res.config.settings'].search([])
    #     vaule = 0
    #     for t in test:
    #         vaule = t.lead_period
    #     _logger.info("test :: %s", test)
    #     # lead_period = self.env['ir.values'].get_default('res.config.settings', 'lead_period')
    #     _logger.info("enter last note 2 :: ", vaule)
    #     date = fields.Date.from_string(self.create_date)
    #     expiry_date = (datetime.today() + relativedelta(days=vaule))
    #     self.date_expiry = expiry_date
    # check_readonly = fields.Boolean(compute='check_sales_groups')
    check_readonly = fields.Boolean(default=False)
    # note = fields.Text(string="Internal Notes (Feedback)", compute="get_expiry_date", store=True)
    source_id = fields.Many2one('utm.source', "Source", required=False)
    meetings_ids = fields.One2many('calendar.event', "opportunity_id")
    customer_id = fields.Many2one('res.partner', string="Customer")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    other = fields.Char("Other")

    def _convert_opportunity_data(self, customer, team_id=False):
        """ Extract the data from a lead to create the opportunity
            :param customer : res.partner record
            :param team_id : identifier of the Sales Team to determine the stage
        """
        _logger.info("I here with data ")
        if not team_id:
            team_id = self.team_id.id if self.team_id else False
        value = {
            'planned_revenue': self.planned_revenue,
            'probability': self.probability,
            'name': self.name,
            'partner_id': customer.id if customer else False,
            'type': 'opportunity',
            'date_open': fields.Datetime.now(),
            'email_from': customer and customer.email or self.email_from,
            'phone': customer and customer.phone or self.phone,
            'date_conversion': fields.Datetime.now(),
        }
        if not self.stage_id:
            stage = self._stage_find(team_id=team_id)
            value['stage_id'] = stage.id
        return value

    def convert_opportunity(self, partner_id, user_ids=False, team_id=False):
        _logger.info("enter crm lead convert_opportunity")
        customer = False
        if partner_id:
            customer = self.env['res.partner'].browse(partner_id)
        for lead in self:
            if not lead.active or lead.probability == 100:
                continue
            vals = lead._convert_opportunity_data(customer, team_id)
            lead.write(vals)

        if user_ids or team_id:
            self.allocate_salesman(user_ids, team_id)

        return True

    # @api.multi
    def name_get(self):
        res = super(CrmLead, self).name_get()
        for val in self:
            if val.type == 'lead':
                name = val.contact_name
                if val.source and name:
                    _logger.info("val.source :: %s",val.source)
                    source = " - " + val.source
                    name = name + source
                    val.name = name
                    res.append((val.id, name))
        return res

    # def check_sales_groups(self):
    #     if self.env.user.has_group('base.group_sale_salesman') or self.env.user.has_group('base.group_sale_manager')or self.env.user.has_group('real_crm_custom.sale_team_leader_group'):
    #         self.check_readonly = True

    @api.onchange('mobile')
    def get_partner_from_mob(self):
        for val in self:
            if val.mobile:
                partner_obj = self.env['res.partner'].search([('mobile', '=', val.mobile)], limit=1)
                if partner_obj:
                    val.partner_id = partner_obj

    # @api.onchange('mobile', 'mobile1_type')
    # @api.constrains('mobile', 'mobile1_type')
    # def validate_mobile_number(self):
    #     for val in self:
    #         if val.mobile and not val.mobile1_type:
    #             raise ValidationError(_("Sorry .. you must choose mobile 1 type !!"))
    #
    #         if val.mobile:
    #             opp_obj = self.search(
    #                 ['&', '|', ('mobile', '=', val.mobile), ('active', '=', True)])
    #
    #             partner_obj = self.env['res.partner'].search(
    #                 ['|', ('mobile', '=', val.mobile)])
    #
    #             mobile = val.mobile
    #
    #             if not (mobile.isdigit()):
    #                 raise ValidationError(_("Sorry .. mobile 1 number must contain integers only !!"))
    #
    #             if len(mobile) != 11 and val.mobile1_type == 'local':
    #                 raise ValidationError(_("Sorry .. mobile 1 number must be 11 digit !!"))
    #
    #             if len(mobile) < 11 and val.mobile1_type == 'foreign':
    #                 raise ValidationError(_("Sorry .. mobile 1 number must be at least 11 digit !!"))
    #
    #             if len(opp_obj) > 1:
    #                 raise ValidationError(_("Sorry .. this mobile 1 number is already exist !!"))
    #             if partner_obj:
    #                 raise ValidationError(_("This mobile 1 is already exist with customer %s") % partner_obj[0].name)




    @api.constrains('contact_name', 'email_from')
    def _check_customer(self):
        for rec in self:
            if rec.contact_name or rec.email_from:
                search_objs = self.search([('contact_name', '=', rec.contact_name),
                                           ('email_from', '=', rec.email_from)])
                if len(search_objs) > 1:
                    raise ValidationError(_('There is already Lead with the same data'))

    # @api.multi
    @api.onchange('project_id')
    def on_change_project(self):
        for rec in self:
            rec.phase_id = False
            rec.unit_ids = False
            all_phases = []
            phases = self.env['project.phase'].search(
                [('project_id', '=', rec.project_id.id), ('available', '=', True)])
            for phase in phases:
                all_phases.append(phase.id)
            return {'domain': {'phase_id': [('id', 'in', all_phases)]}}

    # @api.multi
    @api.onchange('phase_id')
    def on_change_phase(self):
        for rec in self:
            all_properties = []
            properties = self.env['product.product'].search([('project_id', '=', rec.project_id.id),
                                                             ('phase_id', '=', rec.phase_id.id),
                                                             ('type', '=', 'property'),
                                                             ('status', '=', 'available')])
            for property in properties:
                all_properties.append(property.id)
            return {'domain': {'property_id': [('id', 'in', all_properties)]}}

    # @api.multi
    def create_reservation(self):
        vals = {}
        new_customer = 0
        for rec in self:
            if not rec.source:
                raise ValidationError(_("Please Add Source"))
            elif not rec.mobile:
                raise ValidationError(_("Please Add Mobile1 Number"))
            # elif not rec.date_expiry:
            #     raise ValidationError(_("Please Add Expiry Date"))
            elif not rec.contact_name:
                raise ValidationError(_("Please Add Contact Name"))
            elif not rec.street:
                raise ValidationError(_("Please Add Street"))
            elif not rec.sales_type:
                raise ValidationError(_("Please Add Sales Type"))
            elif not rec.function:
                raise ValidationError(_("Please Add Job Title"))

            elif not rec.partner_id:
                if rec.partner_name or rec.contact_name:
                    vals.update({'name': rec.partner_name or rec.contact_name,
                                 'street': rec.street,
                                 'street2': rec.street2,
                                 'country_id': rec.country_id.id,
                                 'mobile1_type': rec.mobile1_type,
                                 'mobile': rec.mobile,
                                 'city': rec.city,
                                 'state_id': rec.state_id.id,
                                 'zip': rec.zip,
                                 'customer_rank': 1,
                                 'type': 'contact',
                                 'organization': rec.organization,
                                 'function': rec.function,
                                 'email': rec.email_from,
                                 'user_id': self.env.user.id
                                 })
                new_customer_object = self.env['res.partner'].create(vals)

                new_customer = new_customer_object.id
                rec.partner_id = new_customer

            # users = [user.id for user in rec.user_ids]
            # broker_ids = [broker.id for broker in rec.broker_ids]

            res = self.env['ir.model.data'].get_object_reference('add_real_estate', 'reservation_form_view')
            view_id = res and res[1] or False
            print("rec.project_id.id :: %s",rec.project_id.id)
            ctx = {
                'default_project_id': rec.market_plan_id.project_id.id,
                'default_phase_id': rec.phase_id.id,
                'default_customer_id': rec.partner_id.id or False,
                'default_broker_id': rec.broker_id.id,
                'default_lead_id': rec.id,
                'default_id_no': rec.id_no or False,
                'default_id_type': rec.id_type or False,
                'default_id_photo': rec.id_photo or False,
            }

            return {
                'name': _("Create Reservation"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'res.reservation',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'context': ctx,
            }

    @api.model
    def create(self, vals):
        # set up context used to find the lead's Sales Team which is needed
        # to correctly set the default stage_id
        context = dict(self._context or {})
        if vals.get('type') and not self._context.get('default_type'):
            context['default_type'] = vals.get('type')
        if vals.get('team_id') and not self._context.get('default_team_id'):
            context['default_team_id'] = vals.get('team_id')

        if vals.get('user_id') and 'date_open' not in vals:
            vals['date_open'] = fields.Datetime.now()
        # _logger.info("ids LL datetime.today() %s", self.create_date)
        #             self.date_expiry = (self.create_date + relativedelta(days=lead_period))
        if self.id == False:
            test = self.env['res.config.settings'].search([])
            vaule = 0
            for t in test:
                vaule =  t.lead_period
            vals['date_expiry'] = (datetime.today() + relativedelta(days=vaule))

        partner_id = vals.get('partner_id') or context.get('default_partner_id')
        onchange_values = self._onchange_partner_id_values(partner_id)
        onchange_values.update(vals)  # we don't want to overwrite any existing key
        vals = onchange_values

        result = super(CrmLead, self.with_context(context)).create(vals)
        # Compute new probability for each lead separately
        result._update_probability()
        return result

    market_plan_id = fields.Many2one(comodel_name="market.plan", string="Marketing Plan", required=True, )
    platform_id_market = fields.Many2one(related="market_plan_id.platform_id", string="Platform", required=False, )
    category_id_market = fields.Many2one(related="market_plan_id.category_id", string="Category", required=False, )
    type_id_market = fields.Many2one(related="market_plan_id.type_id", string="Type", required=False, )
    target_id_market = fields.Many2one(related="market_plan_id.target_id", string="Target", required=False, )
    ads_name_market = fields.Text(related="market_plan_id.ads_name",string="Ads Name", required=False, )
    ads_link_market = fields.Char(related="market_plan_id.ads_link",string="Ads Link", required=False, )
    ads_marketing_cost_market = fields.Float(related="market_plan_id.ads_marketing_cost",string="Ads Marketing Cost",  required=False, )
    lead_cost_market = fields.Float(related="market_plan_id.lead_cost",string="Lead Cost",  required=False )
    planned_leads_market = fields.Float(related="market_plan_id.planned_leads",string="Planned Leads",  required=False, )
    actual_leads_market = fields.Float(related="market_plan_id.actual_leads",string="Actual Leads",  required=False, )
    start_palnned_date_market = fields.Date(related="market_plan_id.start_palnned_date",string="Start Planned Date", required=False, )
    end_palnned_date_market = fields.Date(related="market_plan_id.end_palnned_date",string="End Planned Date", required=False, )
    start_actual_date_market = fields.Date(related="market_plan_id.start_actual_date",string="Start Actual Date", required=False, )
    end_actual_date_market = fields.Date(related="market_plan_id.end_actual_date",string="End Actual Date", required=False, )
    owner_id_market = fields.Many2one(related="market_plan_id.owner_id", string="Owner", required=False, )
    project_id_market = fields.Many2one(related="market_plan_id.project_id",string="Project", required=False, )
    lead_type_id_market = fields.Many2one(related="market_plan_id.lead_type_id", string="Lead Type", required=False, )
    is_visit = fields.Boolean(string="Visit",  )
class LeadNotes(models.Model):
    _name = "lead.notes"
    _order = 'create_date desc'

    note = fields.Text('Note', required=True)
    lead_id = fields.Many2one('crm.lead', ondelete="cascade")

    @api.model
    def create(self, values):
        # overridden to automatically invite user to sign up
        user = super(LeadNotes, self).create(values)
        if self.lead_id != False:
            test = self.env['res.config.settings'].search([])
            vaule = 0
            for t in test:
                vaule =  t.lead_period
            _logger.info("test :: %s",test)
            # lead_period = self.env['ir.values'].get_default('res.config.settings', 'lead_period')
            _logger.info("enter last note 2 :: ",vaule)
            date = fields.Date.from_string(self.create_date)
            expiry_date = (datetime.today() + relativedelta(days=vaule))
            self.lead_id.date_expiry = expiry_date
        return user
