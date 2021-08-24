# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class Lead2OpportunityPartner(models.TransientModel):

    _inherit = 'crm.lead2opportunity.partner'

    name = fields.Selection([
        ('convert', 'Convert to Lead'),
        ('merge', 'Merge with existing opportunities')
    ], 'Conversion Action', required=True,readonly=True)
    def _convert_opportunity(self, vals):
        _logger.info("I here opportunity")
        self.ensure_one()

        res = False

        leads = self.env['crm.lead'].browse(vals.get('lead_ids'))
        for lead in leads:
            lead.is_change_lead_welcome =False
            _logger.info("enter _convert_opportunity ")
            self_def_user = self.with_context(default_user_id=self.user_id.id)

            partner_id = False
            if self.action != 'nothing':
                _logger.info("enter _convert_opportunity 2")

                partner_id = self_def_user._create_partner(
                    lead.id, self.action, vals.get('partner_id') or lead.partner_id.id)
            _logger.info("enter _convert_opportunity 3")

            res = lead.convert_opportunity(partner_id, [], False)
            _logger.info("res :: %s",res)
        user_ids = vals.get('user_ids')

        leads_to_allocate = leads
        if self._context.get('no_force_assignation'):
            leads_to_allocate = leads_to_allocate.filtered(lambda lead: not lead.user_id)

        if user_ids:
            leads_to_allocate.allocate_salesman(user_ids, team_id=(vals.get('team_id')))

        return res

    def action_apply(self):
        _logger.info("I here man")
        """ Convert lead to opportunity or merge lead and opportunity and open
            the freshly created opportunity view.
        """
        self.ensure_one()
        values = {
            'team_id': self.team_id.id,
            'is_change_lead_welcome': False,

        }

        if self.partner_id:
            values['partner_id'] = self.partner_id.id

        if self.name == 'merge':
            _logger.info("I here man merge")
            leads = self.with_context(active_test=False).opportunity_ids.merge_opportunity()
            if not leads.active:
                leads.write({'active': True, 'activity_type_id': False, 'lost_reason': False})
            if leads.type == "lead":
                values.update({'lead_ids': leads.ids, 'user_ids': [self.user_id.id]})
                self.with_context(active_ids=leads.ids)._convert_opportunity(values)
            elif not self._context.get('no_force_assignation') or not leads.user_id:
                values['user_id'] = self.user_id.id
                leads.write(values)
        else:
            _logger.info("I here man else" )
            leads = self.env['crm.lead'].browse(self._context.get('active_ids', []))
            # _logger.info("I here man else leads.contact_name :: %s",leads.contact_name )
            # _logger.info("I here man else leads.mobile1_type :: %s",leads.mobile1_type )

            values.update({'lead_ids': leads.ids,
                           'user_ids': [self.user_id.id],
                           'is_change_lead_welcome': False,
                           # 'mobile1_type': leads.mobile1_type,
                           # 'mobile': leads.mobile,
                           })
            _logger.info("values :: %s",values)
            self._convert_opportunity(values)

        return leads[0].redirect_lead_opportunity_view()
    def _create_partner(self, lead_id, action, partner_id):
        _logger.info("enter create partner")
        """ Create partner based on action.
            :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this method in only called by Lead2OpportunityPartner
        #wizard and would probably diserve to be refactored or at least
        #moved to a better place
        if action == 'each_exist_or_create':
            partner_id = self.with_context(active_id=lead_id)._find_matching_partner()
            action = 'create'
            _logger.info("enter create partner 2")
        _logger.info("enter create partner 233")

        result = self.env['crm.lead'].browse(lead_id).handle_partner_assignation(action, partner_id)
        _logger.info("enter create partner3 ::%s ",result)

        return result.get(lead_id)

class Lead2OpportunityMassConvert(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner.mass'

    @api.model
    def default_get(self, fields):
        res = super(Lead2OpportunityMassConvert, self).default_get(fields)
        if 'partner_id' in fields:  # avoid forcing the partner of the first lead as default
            res['partner_id'] = False
        if 'action' in fields:
            res['action'] = 'nothing'
        if 'name' in fields:
            res['name'] = 'convert'
        if 'opportunity_ids' in fields:
            res['opportunity_ids'] = False
        return res
    action = fields.Selection(selection_add=[
        ('nothing', 'Do not link to a customer')
    ], string='Related Customer', required=True,default="nothing" ,readonly=True)