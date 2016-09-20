# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class linkloving_mrp_bom(models.Model):
    _inherit = 'mrp.bom'

    default_code = fields.Char(related='product_tmpl_id.default_code', string=_(u'Internal Reference'), store=True)

    is_pcba = fields.Boolean(compute='_is_pcba', )

    @api.multi
    def _is_pcba(self):
        for r in self:
            r.is_pcba = r.default_code.startswith('64')

    @api.onchange('product_tmpl_id')
    def _onchange_pcba(self):
        print self.product_tmpl_id.default_code
        self.is_pcba = self.product_tmpl_id.default_code.startswith('64')


# 'product_tmpl_id': fields.many2one('product.template', 'Product', domain="[('type', '!=', 'service')]", required=True),
class linkloving_mrp_bom_line(models.Model):
    _inherit = 'mrp.bom.line'

    line_locate = fields.Char(string=_(u'Locate'))


    is_pcba = fields.Boolean(String=_(u'Is Pcba'))




