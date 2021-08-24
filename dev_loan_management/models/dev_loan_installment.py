# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime,date
from dateutil.relativedelta import relativedelta


class dev_loan_installment(models.Model):
    _name = "dev.loan.installment"
    _order = 'loan_id desc, date'
    _description = 'Loan Installment'
    
    name = fields.Char('Name')
    client_id = fields.Many2one('res.partner',string='Borrower')
    loan_id = fields.Many2one('dev.loan.loan',string='Loan',required="1", ondelete='cascade')
    date = fields.Date('Date')
    state = fields.Selection([('unpaid','Unpaid'),('paid','Paid')], string='State', default='unpaid')
    amount = fields.Monetary('Principal Amount')
    interest = fields.Monetary('Interest Amount')
    total_amount = fields.Monetary('EMI', compute='get_total_amount')
    interest_account_id = fields.Many2one('account.account', string='Interest Account')
    installment_account_id = fields.Many2one('account.account', string='Installment Account')
    loan_payment_journal_id = fields.Many2one('account.journal', string='Payment Journal')
    journal_entry_id = fields.Many2one('account.move', string='Journal Entry', copy=False)
    company_id = fields.Many2one('res.company', string='Company')
    payment_date = fields.Date('Payment Date')
    currency_id = fields.Many2one('res.currency', string='Currency')
    loan_state = fields.Selection(related='loan_id.state', string='Loan State')
    
    
    
    def loan_installment_reminder(self):
        mtp =self.env['mail.template']
        ir_model_data = self.env['ir.model.data'] 
        template_id = ir_model_data.get_object_reference('dev_loan_management', 'installment_reminder_email_template')
        template_id = mtp.browse(template_id[1])
        reminder_days = self.env.user.company_id.ins_reminder_days or 0
        date = datetime.now() + relativedelta(days=reminder_days)
        date = date.strftime("%Y-%m-%d")
        installment_ids = self.search([('state','=','unpaid'),('loan_id.state','=','open'),('date','=',date)])
        for installment in installment_ids:
            a= template_id.send_mail(installment.id,True)
            
            
        
    
    @api.depends('amount','interest')
    def get_total_amount(self):
        for line in self:
            line.total_amount = line.amount + line.interest
    
    
    def get_account_move_vals(self):
        vals={
            'date':date.today(),
            'ref':self.name or 'Loan Installment',
            'journal_id':self.loan_payment_journal_id and self.loan_payment_journal_id.id or False,
            'company_id':self.company_id and self.company_id.id or False,
        }
        return vals
    
    
    def get_partner_lines(self):
        vals={
            'partner_id':self.client_id and self.client_id.id or False,
            'account_id':self.client_id.property_account_receivable_id and self.client_id.property_account_receivable_id.id or False,
            'credit':self.total_amount,
            'name':self.name or '/',
            'date_maturity':date.today(),
        }
        return vals
    
    def get_installment_lines(self):
        vals={
            'partner_id':self.client_id and self.client_id.id or False,
            'account_id':self.installment_account_id and self.installment_account_id.id or False,
            'debit':self.amount,
            'name':self.name or '/',
            'date_maturity':date.today(),
        }
        return vals
        
    def get_interest_lines(self):
        vals={
            'partner_id':self.client_id and self.client_id.id or False,
            'account_id':self.interest_account_id and self.interest_account_id.id or False,
            'debit':self.interest,
            'name':self.name or '/',
            'date_maturity':date.today(),
        }
        return vals
        
        
    def set_loan_close(self):
        installment_ids = self.search([('loan_id','=',self.loan_id.id),('state','=','unpaid')])
        if not installment_ids:
            self.loan_id.state = 'close'
    
    
    def unlink(self):
        for installment in self:
            if installment.loan_id.state not in ['cancel','reject'] and not installment._context.get('force_delete'):
                raise ValidationError(_('You can not delete Loan Installment.'))
        return super(dev_loan_installment, self).unlink()
        
        
    def action_paid_installment(self):
        if self.loan_id and self.loan_id.state != 'open':
            raise ValidationError(_("Installment pay after loan Open !!!"))
            
        if not self.loan_payment_journal_id:
            raise ValidationError(_("Please Select Payment Journal !!!"))
            
        if not self.interest_account_id:
            raise ValidationError(_("Please Select Interest Account !!!"))
        
        if not self.installment_account_id:
            raise ValidationError(_("Please Select Installment Account !!!"))
        
        if self.client_id and not self.client_id.property_account_receivable_id:
            raise ValidationError(_("Select Client Receivable Account !!!"))
        account_move_val = self.get_account_move_vals()
        account_move_id = self.env['account.move'].create(account_move_val)
        vals=[]
        if account_move_id:
            val = self.get_partner_lines()
            vals.append((0,0,val))
            val = self.get_installment_lines()
            vals.append((0,0,val))
            val = self.get_interest_lines()
            vals.append((0,0,val))
            account_move_id.line_ids = vals
            self.journal_entry_id = account_move_id and account_move_id.id or False
            self.state = 'paid'
            self.payment_date = date.today()
            self.set_loan_close()
        
            
            


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
