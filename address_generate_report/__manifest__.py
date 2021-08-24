# -*- coding: utf-8 -*-
{
    'name': "Address Generate Report",

    'summary': """
       """,

    'description': """
        * Payslip batch report.
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','hr_payroll'],

    # always loaded
    'data': [
        'views/hr_payslip_run.xml',
    ],
}
