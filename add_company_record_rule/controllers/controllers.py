# -*- coding: utf-8 -*-
# from odoo import http


# class AddCompanyRecordRule(http.Controller):
#     @http.route('/add_company_record_rule/add_company_record_rule/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_company_record_rule/add_company_record_rule/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_company_record_rule.listing', {
#             'root': '/add_company_record_rule/add_company_record_rule',
#             'objects': http.request.env['add_company_record_rule.add_company_record_rule'].search([]),
#         })

#     @http.route('/add_company_record_rule/add_company_record_rule/objects/<model("add_company_record_rule.add_company_record_rule"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_company_record_rule.object', {
#             'object': obj
#         })
