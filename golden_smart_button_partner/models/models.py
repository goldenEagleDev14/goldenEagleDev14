# -*- coding: utf-8 -*-

from odoo import models, fields, api


class resPartner(models.Model):
    _inherit = 'res.partner'

    def action_view_partner_reservation(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.reservation_list_action').read()[0]
        action['domain'] = [
            ('customer_id', '=', self.id),
        ]
        print("action %s", action)
        return action

    counter_reservation = fields.Integer(string="", required=False, compute="_compute_counter_reservation")

    def _compute_counter_reservation(self):
        for rec in self:
            res = self.env['res.reservation'].search(
                [('customer_id', '=', rec.id)])
            rec.counter_reservation = len(res)

    def action_view_partner_payment(self):
        self.ensure_one()
        # Create action.
        action = {
            'name': ('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree',
            'domain': [('partner_id', '=', self.id)],
        }
        return action
        # self.ensure_one()
        # action = self.env.ref('golden_smart_button_partner.payment_list_action_partner')[0]
        # print("action ddddd",action)
        # action['domain'] = [
        #     ('partner_id', '=', self.id),
        # ]
        # print("action %s",action)
        # return action
        # return {
        #     'name': 'Payments',
        #     'view_type': 'form',
        #     'view_mode': 'tree,form',
        #     'res_model': 'account.payment',
        #     'type': 'ir.actions.act_window',
        #     'domain': [('partner_id', '=', self.id)],
        #     # 'context': {'group_by': ['payment_id']}
        # }

    counter_payment = fields.Integer(string="", required=False, compute="_compute_counter_payment")

    def _compute_counter_payment(self):
        for rec in self:
            res = self.env['account.payment'].search(
                [('partner_id', '=', rec.id)])
            rec.counter_payment = len(res)
