# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class ResPartner(models.Model):
    _inherit = 'res.partner'
    pool_count = fields.Float(compute='_pool_count')
    invoice_pool_count = fields.Float(compute='_invoice_pool_count')

    @api.one
    def _pool_count(self):
        pool = self.env['account.pool']
        self.pool_count = pool.search_count([('partner_id', '=', self.id)])

    @api.one
    def _invoice_pool_count(self):
        pool = self.env['account.invoice.pool']
        self.invoice_pool_count = pool.search_count([('partner_id', '=', self.id)])
