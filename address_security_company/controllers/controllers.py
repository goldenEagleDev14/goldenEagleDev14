# -*- coding: utf-8 -*-
# from odoo import http


# class AddressSecurityCompany(http.Controller):
#     @http.route('/address_security_company/address_security_company/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/address_security_company/address_security_company/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('address_security_company.listing', {
#             'root': '/address_security_company/address_security_company',
#             'objects': http.request.env['address_security_company.address_security_company'].search([]),
#         })

#     @http.route('/address_security_company/address_security_company/objects/<model("address_security_company.address_security_company"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('address_security_company.object', {
#             'object': obj
#         })
