# -*- coding: utf-8 -*-
# from odoo import http


# class MaxabContractValidBase(http.Controller):
#     @http.route('/maxab_contract_valid_base/maxab_contract_valid_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/maxab_contract_valid_base/maxab_contract_valid_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('maxab_contract_valid_base.listing', {
#             'root': '/maxab_contract_valid_base/maxab_contract_valid_base',
#             'objects': http.request.env['maxab_contract_valid_base.maxab_contract_valid_base'].search([]),
#         })

#     @http.route('/maxab_contract_valid_base/maxab_contract_valid_base/objects/<model("maxab_contract_valid_base.maxab_contract_valid_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('maxab_contract_valid_base.object', {
#             'object': obj
#         })
