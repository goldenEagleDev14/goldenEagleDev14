# -*- coding: utf-8 -*-
# from odoo import http


# class AddNationalIssueDatePartner(http.Controller):
#     @http.route('/add__national_issue_date_partner/add__national_issue_date_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add__national_issue_date_partner/add__national_issue_date_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add__national_issue_date_partner.listing', {
#             'root': '/add__national_issue_date_partner/add__national_issue_date_partner',
#             'objects': http.request.env['add__national_issue_date_partner.add__national_issue_date_partner'].search([]),
#         })

#     @http.route('/add__national_issue_date_partner/add__national_issue_date_partner/objects/<model("add__national_issue_date_partner.add__national_issue_date_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add__national_issue_date_partner.object', {
#             'object': obj
#         })
