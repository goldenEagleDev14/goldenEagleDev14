# -*- coding: utf-8 -*-
# from odoo import http


# class AddCompanyTeams(http.Controller):
#     @http.route('/add_company_teams/add_company_teams/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_company_teams/add_company_teams/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_company_teams.listing', {
#             'root': '/add_company_teams/add_company_teams',
#             'objects': http.request.env['add_company_teams.add_company_teams'].search([]),
#         })

#     @http.route('/add_company_teams/add_company_teams/objects/<model("add_company_teams.add_company_teams"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_company_teams.object', {
#             'object': obj
#         })
