# -*- coding: utf-8 -*-

from openerp import models, fields, api

class linkloving_sale(models.Model):
    _inherit = 'res.partner'
    # 是否是国外的客户 默认国内
    is_abroad = fields.Boolean(string=u"country", default=False)

    @api.model
    def create(self, vals):
        if not vals.get('internal_code', False):
            vals['internal_code'] = self.env[
                'ir.sequence'].get('partner.internal.code') or '/'
        return super(linkloving_sale, self).create(vals)
