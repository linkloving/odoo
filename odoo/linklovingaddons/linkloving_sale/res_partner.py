# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _


class partner(models.Model):

    """"""

    _inherit = 'res.partner'

    # 是否是国外的客户 默认国内 1
    is_abroad = fields.Boolean(string=u"country", default=False)

    # 判断用户有没有输入internal_code 若没有 我们自动根据 国内/外 客户生成 internal_code
    @api.model
    def create(self, vals):
        if not vals.get('internal_code', False):
            if vals.get('is_abroad'):
                vals['internal_code'] = self.env[
                    'ir.sequence'].get('en.partner.internal.code') or '/'
            else:
                vals['internal_code'] = self.env[
                    'ir.sequence'].get('cn.partner.internal.code') or '/'
        return super(partner, self).create(vals)

