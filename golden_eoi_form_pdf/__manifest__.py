# -*- coding: utf-8 -*-
{
    'name': "golden_eoi_form_pdf",
    'author': "centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Real Estate',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'add_real_estate','golden_template'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'reports/templates.xml',
        'reports/report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
