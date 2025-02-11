# -*- coding: utf-8 -*-
# from odoo import http


# class Equifax(http.Controller):
#     @http.route('/equifax/equifax', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/equifax/equifax/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('equifax.listing', {
#             'root': '/equifax/equifax',
#             'objects': http.request.env['equifax.equifax'].search([]),
#         })

#     @http.route('/equifax/equifax/objects/<model("equifax.equifax"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('equifax.object', {
#             'object': obj
#         })
