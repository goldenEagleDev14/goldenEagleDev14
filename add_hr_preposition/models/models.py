# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    preposition_ids = fields.One2many('hr.preposition', 'employee_id')

    @api.constrains('job_id', 'department_id','parent_id','coach_id','company_id','franchise')
    def _create_preposition_entry(self):
        if self.id:
            data = {
                'employee_id': self.id,
                'date_from': datetime.now().date(),
                'date_to': datetime.now().date(),
                'job_id': self.job_id.id,
                'department_id': self.department_id.id,
                'parent_id': self.parent_id.id,
                'coach_id': self.coach_id.id,
                'company_id': self.company_id.id,
                'franchise': self.franchise.id,
            }
            print(data)
            self.env['hr.preposition'].create(data)


class HrPreposition(models.Model):
    _name = 'hr.preposition'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char()
    date_from = fields.Date()
    date_to = fields.Date()
    job_id = fields.Many2one('hr.job')
    department_id = fields.Many2one('hr.department')
    parent_id = fields.Many2one('hr.employee',string="Department Head")
    coach_id = fields.Many2one('hr.employee',string='Direct Supervisor')
    company_id = fields.Many2one('res.company')
    franchise = fields.Many2one('franchise.type')