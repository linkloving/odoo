# -*- coding: utf-8 -*-
from openerp import http

# class LinklovingHideMenu(http.Controller):
#     @http.route('/linkloving_hide_menu/linkloving_hide_menu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/linkloving_hide_menu/linkloving_hide_menu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('linkloving_hide_menu.listing', {
#             'root': '/linkloving_hide_menu/linkloving_hide_menu',
#             'objects': http.request.env['linkloving_hide_menu.linkloving_hide_menu'].search([]),
#         })

#     @http.route('/linkloving_hide_menu/linkloving_hide_menu/objects/<model("linkloving_hide_menu.linkloving_hide_menu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('linkloving_hide_menu.object', {
#             'object': obj
#         })
