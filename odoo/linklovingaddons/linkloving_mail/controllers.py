# -*- coding: utf-8 -*-
from openerp import http

# class LinklovingMail(http.Controller):
#     @http.route('/linkloving_mail/linkloving_mail/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/linkloving_mail/linkloving_mail/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('linkloving_mail.listing', {
#             'root': '/linkloving_mail/linkloving_mail',
#             'objects': http.request.env['linkloving_mail.linkloving_mail'].search([]),
#         })

#     @http.route('/linkloving_mail/linkloving_mail/objects/<model("linkloving_mail.linkloving_mail"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('linkloving_mail.object', {
#             'object': obj
#         })