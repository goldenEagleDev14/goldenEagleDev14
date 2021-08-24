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


class dev_loan_type(models.Model):
    _name = "dev.loan.type"
    _description = 'Loan Type'
    
    name = fields.Char('Name', required="1", copy=False)
    is_interest_apply = fields.Boolean('Apply Interest')
    interest_mode = fields.Selection([('flat','Flat'),('reducing','Reducing')], string='Interest Mode')
    rate = fields.Float('Rate', required="1")
    proof_ids = fields.Many2many('dev.loan.proof', string='Loan Proof', requied="1", ondelete='RESTRICT')
    loan_amount = fields.Float('Loan Amount Limit', required="1")
    loan_term_by_month = fields.Integer('Loan Term By Month', required="1")
    loan_term_by_quanter = fields.Integer('Loan Term By Quarter', required="1")
    
    loan_account_id = fields.Many2one('account.account', string='Disburse Account', required="1")
    interest_account_id = fields.Many2one('account.account', string='Interest Account', required="1")
    installment_account_id = fields.Many2one('account.account', string='Installment Account', required="1")
    disburse_journal_id = fields.Many2one('account.journal', string='Disburse Journal', required="1")
    loan_payment_journal_id = fields.Many2one('account.journal', string='Payment Journal', required="1")
    
    @api.onchange('is_interest_apply')
    def onchange_is_interest_apply(self):
        if self.is_interest_apply:
            self.interest_mode = 'flat'
        else:
            self.interest_mode = False
    
    @api.constrains('rate','loan_amount','loan_term_by_month', 'loan_term_by_quanter')        
    def check_rate(self):
        if self.is_interest_apply and self.rate <= 0:
            raise ValidationError(_("Interest Rate Must be Positive !!!"))
        
        if self.loan_amount <= 0:
            raise ValidationError(_("Loan Amount Must be Positive !!!"))
        
        if self.loan_term_by_month <= 0:
            raise ValidationError(_("Loan Term By Month Must be Positive !!!"))
            
        if self.loan_term_by_quanter <= 0:
            raise ValidationError(_("Loan Term By Quater Must be Positive !!!"))
            
                

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
