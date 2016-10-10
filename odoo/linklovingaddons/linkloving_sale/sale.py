# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    """"""

    _inherit = 'sale.order'
    tax_id = fields.Many2many('account.tax', required=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    tax_id = fields.Many2many(related='order_id.tax_id', store=True)
