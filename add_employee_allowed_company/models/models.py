# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    allowed_companies = fields.Many2many('res.company')


class HrTermination(models.Model):
    _inherit = 'hr.termination'

    allowed_companies = fields.Many2many('res.company',related='employee_id.allowed_companies')


class HrContract(models.Model):
    _inherit = 'hr.contract'

    allowed_companies = fields.Many2many('res.company',related='employee_id.allowed_companies')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    allowed_companies = fields.Many2many('res.company')

    @api.model
    def create(self, values):
        record = super(HrEmployee, self).create(values)
        if not record.address_home_id:
            record.address_home_id = record.env['res.partner'].sudo().create({'name': record.name,
                                                                            'email': record.work_email,
                                                                            'company_id': record.company_id.id,
                                                                            'company_type': 'person',
                                                                            'ref': record.zk_emp_id,
                                                                            'phone': record.work_phone,
                                                                            })
        return record

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        if 'company_id' in vals:
            if self.address_home_id:
                self.address_home_id.company_id = self.company_id.id
            if self.address_id:
                self.address_id.company_id = self.company_id.id
            contracts = self.env['hr.contract'].sudo().search([('employee_id', '=', self.id)])
            for rec in contracts:
                rec.company_id = self.company_id.id
        if 'allowed_companies' in vals:
            if self.address_home_id:
                self.address_home_id.allowed_companies = [(6,0,self.allowed_companies.ids)]
            if self.address_id:
                self.address_id.allowed_companies = [(6, 0, self.allowed_companies.ids)]
