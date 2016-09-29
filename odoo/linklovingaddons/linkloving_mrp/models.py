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

    def onchange_product_tmpl_id(self, cr, uid, ids, product_tmpl_id, product_qty=0, context=None):
        """ Changes UoM and name if product_id changes.
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        res = {}
        if product_tmpl_id:
            prod = self.pool.get('product.template').browse(cr, uid, product_tmpl_id, context=context)
            res['value'] = {
                'name': prod.name,
                'product_uom': prod.uom_id.id,
                'is_pcba': prod.default_code.startswith('64')
            }
        return res

# 'product_tmpl_id': fields.many2one('product.template', 'Product', domain="[('type', '!=', 'service')]", required=True),
class linkloving_mrp_bom_line(models.Model):
    _inherit = 'mrp.bom.line'

    line_locate = fields.Char(string=_(u'Locate'))


    is_pcba = fields.Boolean(String=_(u'Is Pcba'))


class linkloving_product_product(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [
        ('default_code_uniq', 'unique (default_code)', 'The default code must be unique!')
    ]
