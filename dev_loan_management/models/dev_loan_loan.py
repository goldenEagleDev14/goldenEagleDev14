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
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class dev_loan_loan(models.Model):
    _name = "dev.loan.loan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'
    _description = 'Loan'
    
    name = fields.Char('Name', default='/', copy=False)
    client_id = fields.Many2one('res.partner', domain=[('is_allow_loan','=',True)], required="1", string='Borrower')
    request_date =fields.Date('Request Date', default=fields.Date.today(), required="1")
    approve_date = fields.Date('Approve Date', copy=False)
    disbursement_date = fields.Date('Disbursement Date', copy=False)
    loan_type_id = fields.Many2one('dev.loan.type', string='Loan Type', required="1")
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    loan_amount = fields.Monetary('Loan Amount', required="1")
    is_interest_apply = fields.Boolean(related='loan_type_id.is_interest_apply', string='Apply Interest')
    interest_rate = fields.Float(related='loan_type_id.rate', string='Interest Rate')
    installment_type = fields.Selection([('month','Month'),('quater','Quater')], default='month', required="1")
    loan_term = fields.Integer('Loan Term', required="1")
    interest_mode = fields.Selection(related='loan_type_id.interest_mode', string='Interest Mode')	
    
    state = fields.Selection([('draft','Draft'),
                              ('confirm','Confirm'),
                              ('approve','Approve'),
                              ('disburse','Disburse'),
                              ('open','Open'),
                              ('close','Close'),
                              ('cancel','Cancel'),
                              ('reject','Reject')], string='State', required="1", default='draft', track_visibility='onchange')
    
    
    installment_ids = fields.One2many('dev.loan.installment','loan_id', string='Installments')
    
    total_interest = fields.Monetary('Interest Amount', compute='get_total_interest')
    paid_amount = fields.Monetary('Paid Amount', compute='get_total_interest')
    remaing_amount = fields.Monetary('Remaing Amount', compute='get_total_interest')
    notes = fields.Text('Notes')
    reject_reason = fields.Text('Reject Reason', copy=False)
    reject_user_id = fields.Many2one('res.users','Reject By', copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self:self.env.user.company_id.currency_id.id)
    proof_ids = fields.Many2many('dev.loan.proof', string='Loan Proof') 
    loan_account_id = fields.Many2one('account.account', string='Disburse Account')
    disburse_journal_id = fields.Many2one('account.journal', string='Disburse Journal')
    disburse_journal_entry_id = fields.Many2one('account.move', string='Disburse Account Entry', copy=False)
    loan_url = fields.Char('URL', compute='get_loan_url')
    loan_document_ids = fields.One2many('ir.attachment','res_id', string='Loan Document')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    
    def _compute_attachment_number(self):
        for loan in self:
            loan.attachment_number = len(loan.loan_document_ids.ids)
    
    
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'dev.loan.loan'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'dev.loan.loan', 'default_res_id': self.id}
        return res
        
        
    def get_monthly_interest(self):
        if self.interest_rate and self.loan_term and self.loan_amount and self.installment_type:
            loan_term = self.loan_term
            if self.installment_type == 'quater':
                loan_term = self.loan_term * 3
            k = 12
            i = self.interest_rate / 100
            a = i / k or 0.00 
            b = (1 - (1 / ((1 + (i / k)) ** loan_term))) or 0.00
            emi = ((self.loan_amount * a) / b) or 0.00
            tot_amt = emi * loan_term
            monthly_interest = (tot_amt - self.loan_amount) / loan_term
            return monthly_interest
            
    
    @api.depends('client_id')
    def get_loan_url(self):
        for loan in self:
            loan.loan_url = False
            if loan.client_id:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069')
                if base_url:
                    base_url += '/web/login?db=%s&login=%s&key=%s#id=%s&model=%s' % (
                    self._cr.dbname, '', '', loan.id, 'dev.loan.loan')
                    loan.loan_url = base_url
                    
                    
    @api.depends('installment_ids')
    def get_total_interest(self):
        for loan in self:
            total_interest = 0
            paid_amount = 0
            remaing_amount = 0
            for installment in loan.installment_ids:
                total_interest += installment.interest
                if installment.state == 'paid':
                    paid_amount+= installment.total_amount
                else:
                    remaing_amount += installment.total_amount
            loan.total_interest = total_interest
            loan.paid_amount = paid_amount
            loan.remaing_amount = remaing_amount
    
    
    @api.depends('total_interest','loan_amount')
    def get_total_amount_to_pay(self):
        for loan in self:
            loan.total_amount_to_pay = 0
            loan.total_amount_to_pay = loan.total_interest + loan.loan_amount
    
    def get_loan_account_journal(self):
        interest_account_id = installment_account_id = loan_payment_journal_id = False
        if not self.loan_type_id:
            raise ValidationError(_("Please Select the Loan Type !!!"))
        if self.loan_type_id.interest_account_id:
            interest_account_id = self.loan_type_id.interest_account_id and self.loan_type_id.interest_account_id.id or False
        
        if self.loan_type_id.installment_account_id:
            installment_account_id = self.loan_type_id.installment_account_id and self.loan_type_id.installment_account_id.id or False
        
        if self.loan_type_id.loan_payment_journal_id:
            loan_payment_journal_id = self.loan_type_id.loan_payment_journal_id and self.loan_type_id.loan_payment_journal_id.id or False
            
        return interest_account_id,installment_account_id,loan_payment_journal_id
            
    
    def compute_installment(self,date= False):
        if self.installment_ids:
            for installment in self.installment_ids:
                installment.with_context({'force_delete':True}).unlink()
                
        inc_month = 1
        if self.installment_type == 'quater':
            inc_month = 3
        
        loan_amount = self.loan_amount
        installment_amount = self.loan_amount / self.loan_term
        if self.state == 'draft':
            date = self.request_date
        else:
            date = date
        vals = []
        interest_account_id,installment_account_id,loan_payment_journal_id = self.get_loan_account_journal()
        for i in range(1,self.loan_term+1):
            interest = 0
            if self.loan_type_id.is_interest_apply:
                if self.interest_mode == 'flat':
                    interest = (( loan_amount * self.interest_rate ) / 100 ) / 12
                else:
                    interest = self.get_monthly_interest()
                    
                if self.installment_type == 'quater':
                    interest = interest * 3
            date = date+relativedelta(months=inc_month)
            vals.append((0, 0,{
                'name':'INS - '+self.name+ ' - '+str(i),
                'client_id':self.client_id and self.client_id.id or False,
                'date':date,
                'amount':installment_amount,
                'interest':interest,
                'state':'unpaid',
                'interest_account_id':interest_account_id or False,
                'installment_account_id':installment_account_id or False,
                'loan_payment_journal_id':loan_payment_journal_id or False,
                'currency_id':self.currency_id and self.currency_id.id or False,
            }))
        self.installment_ids = vals
            
            
    @api.constrains('client_id','request_date')
    def check_number_of_client_loan(self):
        if self.client_id and self.request_date:
            no_of_loan_allow = self.client_id.loan_request
            start_date = date(date.today().year, 1, 1)
            start_date = start_date.strftime('%Y-%m-%d')
            end_date = date(date.today().year, 12, 31)
            end_date = end_date.strftime('%Y-%m-%d')
            loan_ids = self.env['dev.loan.loan'].search([('request_date','<=',end_date),('request_date','>=',start_date),('state','not in',['cancel','reject'])])
            
            if len(loan_ids) > no_of_loan_allow:
                raise ValidationError(_("This Borrower allow only %s Loan Request in Year !!!")%(no_of_loan_allow))
            
    
    @api.onchange('loan_type_id','installment_type')
    def onchange_loan_type(self):
        if self.loan_type_id and self.loan_type_id.proof_ids:
            self.proof_ids = [(6,0, self.loan_type_id.proof_ids.ids)]
        else:
            self.proof_ids = False
            
        if self.loan_type_id and self.installment_type:
            if self.installment_type == 'month':
                self.loan_term = self.loan_type_id.loan_term_by_month
            else:
                self.loan_term = self.loan_type_id.loan_term_by_quanter
            
            
    
    @api.constrains('loan_term','loan_amount','loan_type_id', 'installment_type')        
    def check_rate(self):
        if self.loan_term <= 0:
            raise ValidationError(_("Loan Term Must be Positive !!!"))
                
        if self.loan_amount <= 0:
            raise ValidationError(_("Loan Amount Must be Positive !!!"))
                
        if self.loan_type_id and self.installment_type:
            if self.installment_type == 'month':
                if self.loan_term > self.loan_type_id.loan_term_by_month:
                    raise ValidationError(_("Loan Term Must be less then or equal %s Month")%(self.loan_type_id.loan_term_by_month))
            else:
                if self.loan_term > self.loan_type_id.loan_term_by_quanter:
                    raise ValidationError(_("Loan Term Must be less then or equal %s Quator")%(self.loan_type_id.loan_term_by_quanter))
                
        
        if self.loan_type_id and self.loan_amount:
            if self.loan_amount > self.loan_type_id.loan_amount:
                raise ValidationError(_("Loan Amount Must be less then or equal %s Amount")%(self.loan_type_id.loan_amount))
            
    @api.model
    def create(self,vals):
        vals.update({
                    'name':self.env['ir.sequence'].next_by_code('dev.loan.loan') or '/'
                })
        return super(dev_loan_loan,self).create(vals)
    
    
    def get_loan_manager_mail(self):
        group_id = self.env['ir.model.data'].get_object_reference('dev_loan_management', 'group_loan_manager')[1]
        group_id = self.env['res.groups'].browse(group_id)
        email=''
        if group_id:
            for user in group_id.users:
                if user.partner_id and user.partner_id.email:
                    if email:
                        email = email+','+ user.partner_id.email
                    else:
                        email= user.partner_id.email
        return email
        
        
    def action_confirm_loan(self):
        self.compute_installment()
        self.state = 'confirm'
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('dev_loan_management','dev_loan_loan_request')
        mtp = self.env['mail.template']
        template_id = mtp.browse(template_id[1])
        email = self.get_loan_manager_mail()
        template_id.write({'email_to': email})
        template_id.send_mail(self.ids[0], True)
    

    def action_approve_loan(self):
        self.state = 'approve'
        if self.loan_type_id:
            self.loan_account_id = self.loan_type_id.loan_account_id and self.loan_type_id.loan_account_id.id or False
            self.disburse_journal_id = self.loan_type_id.disburse_journal_id and self.loan_type_id.disburse_journal_id.id or False
        self.approve_date = date.today()
        

    def action_set_to_draft(self):
        if self.installment_ids:
            for installment in self.installment_ids:
                installment.unlink()
        self.state = 'draft'
    
    
    

    def get_account_move_vals(self):
        if not self.disburse_journal_id:
            raise ValidationError(_("Select Disburse Journal !!!"))
        vals={
            'date':self.disbursement_date,
            'ref':self.name or 'Loan Disburse',
            'journal_id':self.disburse_journal_id and self.disburse_journal_id.id or False,
            'company_id':self.company_id and self.company_id.id or False,
        }
        return vals
    
    

    def get_credit_lines(self):
        if not self.loan_account_id:
            raise ValidationError(_("Select Disburse Account !!!"))
        vals={
            'partner_id':self.client_id and self.client_id.id or False,
            'account_id':self.loan_account_id and self.loan_account_id.id or False,
            'credit':self.loan_amount,
            'name':self.name or '/',
            'date_maturity':self.disbursement_date,
        }
        return vals
    
    def get_debit_lines(self):
        if self.client_id and not self.client_id.property_account_receivable_id:
            raise ValidationError(_("Select Client Receivable Account !!!"))
        vals={
            'partner_id':self.client_id and self.client_id.id or False,
            'account_id':self.client_id.property_account_receivable_id and self.client_id.property_account_receivable_id.id or False,
            'debit':self.loan_amount,
            'name':self.name or '/',
            'date_maturity':self.disbursement_date,
        }
        return vals
        
        
    
    def action_disburse_loan(self):
        self.disbursement_date = date.today()
        if self.disbursement_date:
            account_move_val = self.get_account_move_vals()
            account_move_id = self.env['account.move'].create(account_move_val)
            vals=[]
            if account_move_id:
                val = self.get_debit_lines()
                vals.append((0,0,val))
                val = self.get_credit_lines()
                vals.append((0,0,val))
                account_move_id.line_ids = vals
                self.disburse_journal_entry_id = account_move_id and account_move_id.id or False
        if self.disburse_journal_entry_id:
            self.state = 'disburse'
        self.compute_installment(self.disbursement_date)
        
    
    
    def action_open_loan(self):
        self.state = 'open'
        
    
    def get_loan_detail_template(self,loan):
        product_table=''
        product_table +='''
                <table border=1 width=80% style='margin-top: 20px;border-collapse: collapse;'>
                <tr>
                 	<th width=100% colspan="5" style='text-align:center;background:#e0e1e2;padding:5px'>Loan Details</th>
                </tr>
                <tr>
                 	<th width=20% style='text-align:center;background:#e0e1e2;padding:5px'>Loan Type</th>
                 	<th width=20% style='text-align:center;background:#e0e1e2;padding:5px'>Disbursement Date</th>
                 	<th width=20% style='text-align:right;background:#e0e1e2;padding:5px'>Loan Amount</th>
                 	<th width=20% style='text-align:right;background:#e0e1e2;padding:5px'>Loan Term</th>
                </tr>
                
                '''
        c_td_start = "<td style='text-align:center;;padding:5px'>"
        r_td_start = "<td style='text-align:right;;padding:5px'>"
        td_end = '</td>'
        product_table += "<tr>" + c_td_start + str(loan.loan_type_id.name) + td_end + c_td_start + str(loan.disbursement_date) + td_end + r_td_start + str(loan.loan_amount) + td_end + r_td_start + str(loan.loan_term) + td_end + "</tr>"
			                
        product_table += '''</table>'''
		
        return product_table
            
        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
