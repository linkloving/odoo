# -*- coding: utf-8 -*-
from openerp import http

# class LinklovingMrp(http.Controller):
#     @http.route('/linkloving_mrp/linkloving_mrp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/linkloving_mrp/linkloving_mrp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('linkloving_mrp.listing', {
#             'root': '/linkloving_mrp/linkloving_mrp',
#             'objects': http.request.env['linkloving_mrp.linkloving_mrp'].search([]),
#         })

#     @http.route('/linkloving_mrp/linkloving_mrp/objects/<model("linkloving_mrp.linkloving_mrp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('linkloving_mrp.object', {
#             'object': obj
#         })