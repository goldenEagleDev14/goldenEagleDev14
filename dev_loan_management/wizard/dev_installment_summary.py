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
import calendar
import itertools
from operator import itemgetter
import operator

class dev_installment_summary(models.TransientModel):
    _name = "dev.installment.summary"
    _description = 'Loan Installment Summary'
    
    @api.model
    def _get_from_date(self):
        date = datetime.now()
        month = date.month
        if date.month < 10:
            month = '0'+str(date.month)
        date = str(date.year)+'-'+str(month)+'-01'
        return date
        
    @api.model
    def _get_to_date(self):
        date = datetime.now()
        m_range = calendar.monthrange(date.year,date.month)
        month = date.month
        if date.month < 10:
            month = '0'+str(date.month)
        date = str(date.year)+'-'+str(month)+'-'+str(m_range[1])
        return date
    
    start_date = fields.Date('Start Date', required="1", default=_get_from_date)
    end_date = fields.Date('End Date', required="1", default=_get_to_date)
    state = fields.Selection([('paid','Paid'),('unpaid','Unpaid')], string='State', default='unpaid')
    group_by = fields.Selection([('date','Date'),('loan','Loan'),('borrower','Borrower')], string='Group By', default='date')
    
    def action_print_pdf(self):
        data={}
        data['form'] = self.read()[0]
        return self.env.ref('dev_loan_management.print_installment_summary').report_action(self, data=None)
        
    
    
    def get_lines(self):
        installment_ids = self.get_installment()
        if installment_ids:
            lst = []
            for installment in installment_ids:
                if installment.date:
                    date = installment.date.strftime("%d-%m-%Y")
                lst.append({
                    'name':installment.name,
                    'loan':installment.loan_id.name,
                    'date':date,
                    'borrower':installment.client_id.name,
                    'state':installment.state,
                    'pri_amount':installment.amount,
                    'interest':installment.interest,
                    'emi':installment.total_amount,
                    'currency_id':installment.currency_id,
                })
            
            n_lines=sorted(lst,key=itemgetter(self.group_by))
            groups = itertools.groupby(n_lines, key=operator.itemgetter(self.group_by))
            lines = [{'group':k,'values':[x for x in v]} for k, v in groups] 
            return lines
        return []

    
    def get_installment(self):
        installment_ids = self.env['dev.loan.installment'].search([('date','<=',self.end_date),('date','>=',self.start_date),('state','=',self.state)])
        return installment_ids
    
    
    def action_view_summary(self):
        installment_ids = self.get_installment()
        if installment_ids:
            action = self.env.ref('dev_loan_management.action_dev_loan_installment').read()[0]
            action['domain'] = [('id', 'in', installment_ids.ids)]
            if self.group_by == 'loan':
                action[('context')] = {'search_default_loan_id':1}
            elif self.group_by == 'date':
                action[('context')] = {'search_default_date':1}
            else:
                action[('context')] = {'search_default_client_id':1}
                
            return action
        else:
            action = {'type': 'ir.actions.act_window_close'}
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
    
