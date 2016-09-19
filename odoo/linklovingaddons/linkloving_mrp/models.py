# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class linkloving_mrp_bom(models.Model):
    _inherit = 'mrp.bom'

    default_code = fields.Char(related='product_tmpl_id.default_code', string=_(u'Internal Reference'), store=True)

# 'product_tmpl_id': fields.many2one('product.template', 'Product', domain="[('type', '!=', 'service')]", required=True),
