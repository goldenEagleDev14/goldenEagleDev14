# -*- coding: utf-8 -*-
# from odoo import http


# class AddCompanyNameBranch(http.Controller):
#     @http.route('/add_company_name_branch/add_company_name_branch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_company_name_branch/add_company_name_branch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_company_name_branch.listing', {
#             'root': '/add_company_name_branch/add_company_name_branch',
#             'objects': http.request.env['add_company_name_branch.add_company_name_branch'].search([]),
#         })

#     @http.route('/add_company_name_branch/add_company_name_branch/objects/<model("add_company_name_branch.add_company_name_branch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_company_name_branch.object', {
#             'object': obj
#         })
