# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.osv import osv


class PurchaseOrder(models.Model):
    """
    采购单
    """
    _inherit = 'purchase.order'
    pre_payment_ids = fields.One2many('account.prepayment', 'po_id')
    prepayment_count = fields.Char(compute='get_pre_payment_ids')
    is_prepayment_deduct = fields.Boolean()
    pre_payment_mount = fields.Float(compute='get_pre_payment_mount')

    def get_pre_payment_mount(self):
        self.pre_payment_mount = 0
        for p in self.pre_payment_ids:
            self.pre_payment_mount += p.amount




    @api.multi
    def get_pre_payment_ids(self):
        for po in self:
            po.prepayment_count = len(po.pre_payment_ids)

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

    def action_picking_create(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids):
            picking_vals = {
                'picking_type_id': order.picking_type_id.id,
                'partner_id': order.partner_id.id,
                'date': order.date_order,
                'origin': order.name,
                'po_id': order.id
            }
            picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)
            self._create_stock_moves(cr, uid, order, order.order_line, picking_id, context=context)
        return picking_id

    def prepayment_open(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'linkloving_account', 'action_invoice_prepayment')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        pre_payment_ids = []
        for po in self.browse(cr, uid, ids, context=context):
            pre_payment_ids += [pre_payment.id for pre_payment in po.pre_payment_ids]
        if not pre_payment_ids:
            raise osv.except_osv(_('Error!'), _('Please create Invoices.'))
            # choose the view_mode accordingly
            result['domain'] = "[('id','in',[" + ','.join(map(str, pre_payment_ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'linkloving_account', 'purchase_pre_payment_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pre_payment_ids and pre_payment_ids[0] or False
        return result


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    po_id = fields.Many2one('purchase.order')
    pre_payment_ids = fields.One2many('account.prepayment', related='po_id.pre_payment_ids')
    pre_payment_amount = fields.Float(string='Pre Payment Amount')
