# -*- coding: utf-8 -*-
from openerp import http

# class Testaddon(http.Controller):
#     @http.route('/testaddon/testaddon/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/testaddon/testaddon/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('testaddon.listing', {
#             'root': '/testaddon/testaddon',
#             'objects': http.request.env['testaddon.testaddon'].search([]),
#         })

#     @http.route('/testaddon/testaddon/objects/<model("testaddon.testaddon"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('testaddon.object', {
#             'object': obj
#         })