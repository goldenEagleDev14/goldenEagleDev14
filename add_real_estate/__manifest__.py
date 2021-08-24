# -*- coding: utf-8 -*-
{
    'name': "add_real_estate",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full listproduct
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','project','product','web','web_widget_google_maps','analytic','account','sale','check_management','account_batch_payment','add_user_name_branch','add_company_teams','add__national_issue_date_partner'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/merge_view.xml',
        'wizard/cancel_res_views.xml',
        'views/menus.xml',
        'views/address_fill_payment_lines_wizard.xml',
        'views/phase_views.xml',
        'views/property_view.xml',
        'views/custom_tables_view.xml',
        'views/image_view.xml',
        'views/history_views.xml',
        'views/action_server_view.xml',
        'views/city_country_views.xml',
        'views/request_reservation.xml',
        'views/res_reservation.xml',
        'views/partners_view.xml',
        'views/sequence.xml',
        'views/address_pay_strategy.xml',
        'views/customer_payment.xml',
        'views/payment_view_inherit.xml',
        'views/release_unit.xml',
        'views/transfer_unit.xml',
        'views/project_views.xml',
        'views/contract_view.xml',
        'views/templates.xml',
        'views/Accessories.xml',
        'views/payement_strg.xml',
        # 'views/views.xml',

        # 'views/res_company_views.xml',
        # 'views/res_user_views.xml',
        'views/payment_term_line_views.xml',
        # 'views/view_batch_payment.xml',
        'views/commission_view.xml',
        'views/commission_account_wizard.xml',
        'views/vendor_normal_deposit.xml',
        'views/company_team_views.xml',
        'views/payment_line_type_view.xml',
        'report/report_header_footer_base.xml',
        'report/report_reservation.xml',
        'report/report_reservation_base.xml',
        'report/report_sample.xml',
        'report/report_payment_strg_request.xml',
        'report/report_saledetails_test.xml',
        'report/report_payment_base.xml',
        'report/report_customer_payment_base.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}