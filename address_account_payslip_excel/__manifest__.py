# -*- coding: utf-8 -*-
{
    'name': "address_account_payslip_excel",

    'summary': """
        """,

    'description': """
    """,

    'author': "Centione",
    'website': "www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','hr_payroll','centione_hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_payslip_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}