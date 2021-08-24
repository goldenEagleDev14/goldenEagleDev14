# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Warning_discount_wizard(models.TransientModel):

    _name = 'warning.discount.wizard'

    pool_exceed = fields.Text()
    min_limit = fields.Text()
    max_limit = fields.Text()
    centeral_percentage = fields.Text()


    @api.model
    def create(self, values):
        # Add code here
        # if values["centeral_percentage"] == "":
        #     values["centeral_percentage"] = False
        if values["max_limit"] =="":
            values["max_limit"] = False
        if values["min_limit"] == "":
            values["min_limit"] = False
        if values["pool_exceed"]=="":
            values["pool_exceed"] = False
        if values["centeral_percentage"] == "":
                values["centeral_percentage"] = False

        return super(Warning_discount_wizard, self).create(values)



    def force_discount_check(self):

        active_id = self._context['active_id']
        abd = self.env['account.batch.payment'].browse(active_id)
        abd.discount_all()

