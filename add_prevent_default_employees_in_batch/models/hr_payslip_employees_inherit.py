# -*- coding: utf-8 -*-

from odoo import models, fields, api

class hr_payslip_employees_inherit(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
                                    default=None,required=True)
