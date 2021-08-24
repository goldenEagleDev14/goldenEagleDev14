# -*- coding: utf-8 -*-

from odoo import models, fields, api

class hr_payslip_inherit(models.Model):
    _inherit = 'hr.payslip'


    archived_employee=fields.Boolean(string='Archived Employee', related='employee_id.active')
    completed_docs=fields.Boolean(string='Completed Docs', related='employee_id.completed_docs')
    not_completed_docs=fields.Boolean(string='Not Completed Docs', related='employee_id.not_completed_docs')
    zk_emp_id=fields.Char(string='Employee Attendance Id', related='employee_id.zk_emp_id')
    termination_date = fields.Date(string="Employee Termination Date", related='employee_id.termination_date',
                                    )






