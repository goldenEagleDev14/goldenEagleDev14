# -*- coding: utf-8 -*-
# from odoo import http


# class AddCreatePartnerInEmployee(http.Controller):
#     @http.route('/add_create_partner_in_employee/add_create_partner_in_employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_create_partner_in_employee/add_create_partner_in_employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_create_partner_in_employee.listing', {
#             'root': '/add_create_partner_in_employee/add_create_partner_in_employee',
#             'objects': http.request.env['add_create_partner_in_employee.add_create_partner_in_employee'].search([]),
#         })

#     @http.route('/add_create_partner_in_employee/add_create_partner_in_employee/objects/<model("add_create_partner_in_employee.add_create_partner_in_employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_create_partner_in_employee.object', {
#             'object': obj
#         })
