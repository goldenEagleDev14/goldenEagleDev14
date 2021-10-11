# -*- coding: utf-8 -*-
# from odoo import http


# class AddReservationUnitChanges(http.Controller):
#     @http.route('/add_reservation_unit_changes/add_reservation_unit_changes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_reservation_unit_changes/add_reservation_unit_changes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_reservation_unit_changes.listing', {
#             'root': '/add_reservation_unit_changes/add_reservation_unit_changes',
#             'objects': http.request.env['add_reservation_unit_changes.add_reservation_unit_changes'].search([]),
#         })

#     @http.route('/add_reservation_unit_changes/add_reservation_unit_changes/objects/<model("add_reservation_unit_changes.add_reservation_unit_changes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_reservation_unit_changes.object', {
#             'object': obj
#         })
