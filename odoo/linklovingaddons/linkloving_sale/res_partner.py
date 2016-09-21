# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _


class partner(models.Model):

    """"""

    _inherit = 'res.partner'

    # 是否是国外的客户 默认国内
    is_abroad = fields.Boolean(string=u"country", default=False)

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

    # _sql_constraints = {
    #     ('internal_code_uniq', 'unique(internal_code)',
    #         'Internal Code mast be unique!')
    # }
