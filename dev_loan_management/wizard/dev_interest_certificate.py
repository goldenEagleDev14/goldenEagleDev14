# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime

class dev_interest_certificate(models.TransientModel):
    _name = "dev.interest.certificate"
    _description = 'Loan Interest Certificate'
    
    
    client_id = fields.Many2one('res.partner', domain=[('is_allow_loan','=',True)], required="1", string='Borrower')
    loan_id = fields.Many2one('dev.loan.loan', string='Loan', required="1")
    start_date = fields.Date('Start Date', required="1")
    end_date = fields.Date('End Date', required="1")
    
    
    def action_print_pdf(self):
        data={}
        data['form'] = self.read()[0]
        return self.env.ref('dev_loan_management.print_interest_certificate').report_action(self, data=None)
        
    
    
    def get_lines(self):
        installment_ids = self.env['dev.loan.installment'].search([('loan_id','=',self.loan_id.id),
                                                                   ('client_id','=',self.client_id.id),
                                                                   ('date','<=',self.end_date),('date','>=',self.start_date),
                                                                   ('state','=','paid')])
        lst = []
        for installment in installment_ids:
            if installment.date:
                date = installment.date.strftime("%d-%m-%Y")
            lst.append({
                'name':installment.name,
                'date':date,
                'pri_amount':installment.amount,
                'interest':installment.interest,
                'emi':installment.total_amount,
                'currency_id':installment.currency_id,
            })
        return lst
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
    
