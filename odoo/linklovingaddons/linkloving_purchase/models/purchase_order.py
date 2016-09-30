# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class PurchaseOrder(models.Model):
    """
    供应商资质等级
    """
    _inherit = 'purchase.order'
    pre_payment_ids = fields.One2many('account.prepayment', 'po_id')

    @api.multi
    def create_prepayment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Pre Payment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.prepayment',
            'view_id': self.env.ref('linkloving_account.purchase_pre_payment_form_modal').id,
            'context': {'default_po_id': self.id},
            'target': 'new',
        }


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    po_id = fields.Many2one('purchase.order')
    pre_payment_ids = fields.One2many('account.prepayment', related='po_id.pre_payment_ids')
    pre_payment_amount = amount = fields.Float(string='Pre Payment Amount')
