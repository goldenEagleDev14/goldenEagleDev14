# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Customer / Supplier Loan Management',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'Accounting',
    'description':
        """
        This Module help to create loan of customer or Supplier
Customer Supplier loan management
Odoo Customer Supplier loan management
Customer Supplierloan
Odoo Customer Supplier loan
 loan for Customer Supplier
Customer Supplier loan approval functionality 
Loan Installment link with Customer Supplier
Loan notification Customer/Supplier Inbox
Loan Deduction in Customer/Supplier
Manage Customer/Supplier loan 
Manage Customer/Supplier loan odoo
Manage loan for Customer/Supplier
Manage loan for Customer/Supplier odoo
Loan management 
Odoo loan management
Odoo loan management system
Odoo loan management app
helps you to create customized loan
 module allow Manager to manage loan of Customer/Supplier
Loan Request and Approval
Odoo Loan Report
create different types of loan for Customer/Supplier
allow user to configure loan given to Customer/Supplier will be interest payable or not.
Open Customer/Supplier Loan Management
Loan accounting
Odoo loan accounting
Customer/Supplier can create loan request.
Manage Customer/Supplier Loan and Integrated with Accouting  
Customer loan management 
Odoo customer loan management 
Supplier loan management 
Odoo supplier loan management 
Manage loan management 
Manage customer loan management
Odoo manage loan management
Odoo manage customer loan management 
Easy loan management workflow Define Loan Type
Manage supplier loan management 
Odoo manage supplier loan management 
Odoo Easy loan management workflow Define Loan Type
Add different loan types
Odoo Add different loan types
Add Loan Proofs or Required Documents List
Odoo Add Loan Proofs or Required Documents List
Loan Account Based on Loan Type
Odoo Loan Account Based on Loan Type
Send Confirmation Notification to Loan Manager
Odoo Send Confirmation Notification to Loan Manager
Manager can Approve Loan Request
Odoo Manager can Approve Loan Request
 Loan PDF Report
Odoo  Loan PDF Report
Manage  Loan PDF Report
Odoo manage  Loan PDF Report
Loan Summary PDF Report
Odoo Loan Summary PDF Report
Manage Loan Summary PDF Report
Odoo manage Loan Summary PDF Report


    """,
    'summary': 'odoo app manage Customer / Supplier Loan Management, Customer Loan, Supplier Loan, vendor Loan, Loan Type, Loan Proef, Loan type, Loan Request, Notification, Loan Document, Loan installment, Loan Disbursement, Customer Loan Process, Loan emi',
    'depends': ['mail','account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron.xml',
        'edi/mail_template.xml',
        'views/dev_loan_menu.xml',
        'views/dev_loan_proof_view.xml',
        'views/dev_loan_type.xml',
        'views/res_partner_view.xml',
        'wizard/dev_loan_reject_view.xml',
        'wizard/dev_installment_summary_views.xml',
        'wizard/dev_interest_certificate_views.xml',
        'views/dev_loan_view.xml',
        'views/dev_loan_installment_view.xml',
        'report/report_header.xml',
        'report/report_print_loan.xml',
        'report/installment_summary_template.xml',
        'report/interest_certificate_template.xml',
        'report/report_menu.xml',
        'views/res_config_settings_view.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':49.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
