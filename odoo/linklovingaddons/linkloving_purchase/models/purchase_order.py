# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class PurchaseOrder(models.Model):
    """
    供应商资质等级
    """
    _inherit = 'purchase.order'

    @api.multi
    def create_prepayment(self):
        print self.id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Pre Payment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.prepayment',
            'context': {'default_po_id': self.id},
            'target': 'new',
        }
