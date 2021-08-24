# -*- coding: utf-8 -*-
# from odoo import http


# class GoldenSmartButtonPartner(http.Controller):
#     @http.route('/golden_smart_button_partner/golden_smart_button_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/golden_smart_button_partner/golden_smart_button_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('golden_smart_button_partner.listing', {
#             'root': '/golden_smart_button_partner/golden_smart_button_partner',
#             'objects': http.request.env['golden_smart_button_partner.golden_smart_button_partner'].search([]),
#         })

#     @http.route('/golden_smart_button_partner/golden_smart_button_partner/objects/<model("golden_smart_button_partner.golden_smart_button_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('golden_smart_button_partner.object', {
#             'object': obj
#         })
