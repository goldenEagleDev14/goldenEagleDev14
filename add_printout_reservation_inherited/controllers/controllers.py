# -*- coding: utf-8 -*-
# from odoo import http


# class AddPrintoutReservationInherited(http.Controller):
#     @http.route('/add_printout_reservation_inherited/add_printout_reservation_inherited/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_printout_reservation_inherited/add_printout_reservation_inherited/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_printout_reservation_inherited.listing', {
#             'root': '/add_printout_reservation_inherited/add_printout_reservation_inherited',
#             'objects': http.request.env['add_printout_reservation_inherited.add_printout_reservation_inherited'].search([]),
#         })

#     @http.route('/add_printout_reservation_inherited/add_printout_reservation_inherited/objects/<model("add_printout_reservation_inherited.add_printout_reservation_inherited"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_printout_reservation_inherited.object', {
#             'object': obj
#         })
