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


class dev_loan_reject(models.TransientModel):
    _name = "dev.loan.reject"
    _description = 'Loan Reject'
    
    reason = fields.Text('Reason', required="1")
    
    
    def action_reject_loan(self):
        active_ids = self._context.get('active_ids')
        loan_ids = self.env['dev.loan.loan'].browse(active_ids)
        ir_model_data = self.env['ir.model.data']
        mtp = self.env['mail.template']
        for loan in loan_ids:
            loan.reject_reason = self.reason
            loan.state = 'reject'
            loan.reject_user_id = self.env.user.id
            template_id = ir_model_data.get_object_reference('dev_loan_management','dev_loan_loan_request_reject')
            template_id = mtp.browse(template_id[1])
            template_id.send_mail(loan.id, True)

            

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
    
