# -*- coding: utf-8 -*-
# from odoo import http


# class AddNotesCustomerPartner(http.Controller):
#     @http.route('/add_notes_customer_partner/add_notes_customer_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_notes_customer_partner/add_notes_customer_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_notes_customer_partner.listing', {
#             'root': '/add_notes_customer_partner/add_notes_customer_partner',
#             'objects': http.request.env['add_notes_customer_partner.add_notes_customer_partner'].search([]),
#         })

#     @http.route('/add_notes_customer_partner/add_notes_customer_partner/objects/<model("add_notes_customer_partner.add_notes_customer_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_notes_customer_partner.object', {
#             'object': obj
#         })
