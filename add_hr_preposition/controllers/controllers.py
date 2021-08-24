# -*- coding: utf-8 -*-
# from odoo import http


# class ExpressPreposition(http.Controller):
#     @http.route('/express_preposition/express_preposition/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/express_preposition/express_preposition/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('express_preposition.listing', {
#             'root': '/express_preposition/express_preposition',
#             'objects': http.request.env['express_preposition.express_preposition'].search([]),
#         })

#     @http.route('/express_preposition/express_preposition/objects/<model("express_preposition.express_preposition"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('express_preposition.object', {
#             'object': obj
#         })
