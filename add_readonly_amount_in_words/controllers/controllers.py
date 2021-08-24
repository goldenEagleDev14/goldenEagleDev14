# -*- coding: utf-8 -*-
# from odoo import http


# class AddReadonlyAmountInWords(http.Controller):
#     @http.route('/add_readonly_amount_in_words/add_readonly_amount_in_words/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_readonly_amount_in_words/add_readonly_amount_in_words/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_readonly_amount_in_words.listing', {
#             'root': '/add_readonly_amount_in_words/add_readonly_amount_in_words',
#             'objects': http.request.env['add_readonly_amount_in_words.add_readonly_amount_in_words'].search([]),
#         })

#     @http.route('/add_readonly_amount_in_words/add_readonly_amount_in_words/objects/<model("add_readonly_amount_in_words.add_readonly_amount_in_words"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_readonly_amount_in_words.object', {
#             'object': obj
#         })
