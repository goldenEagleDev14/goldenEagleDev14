# -*- coding: utf-8 -*-
# from odoo import http


# class AddChangeEmployeeCompany(http.Controller):
#     @http.route('/add_change_employee_company/add_change_employee_company/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_change_employee_company/add_change_employee_company/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_change_employee_company.listing', {
#             'root': '/add_change_employee_company/add_change_employee_company',
#             'objects': http.request.env['add_change_employee_company.add_change_employee_company'].search([]),
#         })

#     @http.route('/add_change_employee_company/add_change_employee_company/objects/<model("add_change_employee_company.add_change_employee_company"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_change_employee_company.object', {
#             'object': obj
#         })
