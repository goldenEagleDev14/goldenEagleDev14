# -*- coding: utf-8 -*-
from odoo import http

# class AddRealEstate(http.Controller):
#     @http.route('/add_real_estate/add_real_estate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_real_estate/add_real_estate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_real_estate.listing', {
#             'root': '/add_real_estate/add_real_estate',
#             'objects': http.request.env['add_real_estate.add_real_estate'].search([]),
#         })

#     @http.route('/add_real_estate/add_real_estate/objects/<model("add_real_estate.add_real_estate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_real_estate.object', {
#             'object': obj
#         })