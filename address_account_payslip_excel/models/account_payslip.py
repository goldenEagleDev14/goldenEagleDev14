# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPayslip(models.Model):
    _name = 'account.payslip'
    _rec_name = 'name'
    _description = 'get excel report from hr.payslip'

    name = fields.Char('Patch Name',readonly=True)
    report = fields.Binary(string='Download', readonly=True)
    payslip_run_id = fields.Many2one(comodel_name="hr.payslip.run")
    # date_start = fields.Date(string="Date From", required=True, )
    # date_end = fields.Date(string="Date To", required=True, )
    # company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True)