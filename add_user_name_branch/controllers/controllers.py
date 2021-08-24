# -*- coding: utf-8 -*-
# from odoo import http


# class AddUserNameBranch(http.Controller):
#     @http.route('/add_user_name_branch/add_user_name_branch/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_user_name_branch/add_user_name_branch/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_user_name_branch.listing', {
#             'root': '/add_user_name_branch/add_user_name_branch',
#             'objects': http.request.env['add_user_name_branch.add_user_name_branch'].search([]),
#         })

#     @http.route('/add_user_name_branch/add_user_name_branch/objects/<model("add_user_name_branch.add_user_name_branch"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_user_name_branch.object', {
#             'object': obj
#         })
