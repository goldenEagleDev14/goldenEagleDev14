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


class dev_loan_proof(models.Model):
    _name = "dev.loan.proof"
    _description = 'Loan Proof'
    
    name = fields.Char('Name', required="1", copy=False)
    is_required= fields.Boolean('Required')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
