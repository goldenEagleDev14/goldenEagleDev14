# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class ChangePropertyStatus(models.TransientModel):
    _name = 'change.property.status'

    # @api.multi
    def get_all_sales_persons(self):
        res_user_obj = self.env['res.users'].search([])
        user_list = []
        for user in res_user_obj:
            if user.has_group('base.group_sale_salesman') or user.has_group('sky_height.sale_team_leader_group'):
                user_list.append(user.id)
        return [('id', 'in', user_list)]

    product_id = fields.Many2one('product.product', string='Property')
    user_id = fields.Many2one('res.users', string='User', domain=get_all_sales_persons)

    # @api.multi
    def action_done(self):
        for val in self:
            if val.product_id:
                val.product_id.sudo().write({'resp_user_id': val.user_id.id})
                val.product_id.sudo().update_state_to_not_available()
