# -*- coding: utf-8 -*-
# from odoo import http


# class AddResPartnerEmployee(http.Controller):
#     @http.route('/add_res_partner_employee/add_res_partner_employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_res_partner_employee/add_res_partner_employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_res_partner_employee.listing', {
#             'root': '/add_res_partner_employee/add_res_partner_employee',
#             'objects': http.request.env['add_res_partner_employee.add_res_partner_employee'].search([]),
#         })

#     @http.route('/add_res_partner_employee/add_res_partner_employee/objects/<model("add_res_partner_employee.add_res_partner_employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_res_partner_employee.object', {
#             'object': obj
#         })
