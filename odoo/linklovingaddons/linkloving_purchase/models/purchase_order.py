# -*- coding: utf-8 -*-
import logging
import threading

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp import tools
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    """
    采购单
    """
    _inherit = 'purchase.order'

    pre_payment_ids = fields.One2many('account.payment', 'po_id')
    prepayment_count = fields.Char(compute='get_pre_payment_ids')
    is_prepayment_deduct = fields.Boolean()
    pre_payment_mount = fields.Float(compute='get_pre_payment_mount')
    product_count = fields.Float(compute='get_product_count')

    def get_product_count(self):
        count = 0.0
        for line in self.order_line:
            count += line.product_qty
        self.product_count = count

    def get_pre_payment_mount(self):
        self.pre_payment_mount = 0
        for p in self.pre_payment_ids:
            self.pre_payment_mount += p.amount

    # @api.multi
    # def write(self, vals):
    #     cur_purchase_order_line = self.order_line
    #     order_line_list_to_delete = []
    #     for r in cur_purchase_order_line:
    #         if r.product_id.seller_ids:
    #             r.unlink()
    #     return super(PurchaseOrder, self).write(vals)

    @api.one
    def check_product_has_supplier(self):
        is_exception_order = self.partner_id == self.env.ref('linkloving_purchase.res_partner_exception_supplier')
        if not is_exception_order:
            return
        for r in self.order_line:
            if r.product_id.seller_ids:
                id_to_delete = r.id
                proc_obj = self.env['procurement.order'].search([('purchase_line_id','=',id_to_delete)])
                r.unlink()
                if proc_obj:
                    proc_obj.run()
        if not self.order_line:
            self.unlink()

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
            'res_model': 'account.payment',
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


class LinklovingPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    sequence = fields.Integer(string='序号')

    def default_get(self, cr, uid, ids, context=None):
        res = super(LinklovingPurchaseOrderLine, self).default_get(cr, uid, ids, context=None)
        print context
        if context:
            context_keys = context.keys()
            next_sequence = 1
            if 'order_line' in context_keys:
                if len(context.get('order_line')) > 0:
                    next_sequence = len(context.get('order_line')) + 1
        res.update({'sequence': next_sequence})
        return res


    @api.multi
    def action_open_product_detail(self):
        print self.env.ref('product.product_template_only_form_view').id,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Modify Product',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.template',
            'view_id': self.env.ref('linkloving_purchase.linkloving_product_product_form_view').id,
            'res_id': self.product_id.product_tmpl_id.id,
            'context': {'is_show': True},
            'target': 'new',
        }

    @api.one
    def unlink(self):
        is_exception_order = self.order_id.partner_id == self.env.ref('linkloving_purchase.res_partner_exception_supplier')
        if not is_exception_order:
            return super(LinklovingPurchaseOrderLine, self).unlink()
        else:
            if self.product_id.seller_ids:
                id_to_delete = self.id
                proc_obj = self.env['procurement.order'].search([('purchase_line_id', '=', id_to_delete)])
                super(LinklovingPurchaseOrderLine, self).unlink()
                if proc_obj:
                    proc_obj.run()
                # if not self.order_id.order_line:
                #     self.order_id.unlink()
            else:
                raise osv.except_osv(_('Error!'),_('该产品还未设置供应商，不可从订单中删除'))

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    po_id = fields.Many2one('purchase.order')
    pre_payment_ids = fields.One2many('account.payment', related='po_id.pre_payment_ids')
    pre_payment_amount = fields.Float(string='Pre Payment Amount')


class linkloving_procurement_order(models.Model):
    _inherit = 'procurement.order'

    def _get_product_supplier(self, cr, uid, procurement, context=None):
        supplierinfo = self.pool['product.supplierinfo']
        company_supplier = supplierinfo.search(cr, uid,
                                               [('product_tmpl_id', '=', procurement.product_id.product_tmpl_id.id),
                                                ('company_id', '=', procurement.company_id.id)], limit=1,
                                               context=context)
        if company_supplier:
            return supplierinfo.browse(cr, uid, company_supplier[0], context=context).name
        elif procurement.product_id.seller_id:
            return procurement.product_id.seller_id
        else:
            return self.pool['ir.model.data'].get_object(
                cr, uid, 'linkloving_purchase', 'res_partner_exception_supplier', context=context)

            # @api.model
            # def _get_product_supplier(self, procurement,):
            #     supplierinfo = self.env['product.supplierinfo']
            #     company_supplier = supplierinfo.search(
            #                                            [('product_tmpl_id', '=', procurement.product_id.product_tmpl_id.id),
            #                                             ('company_id', '=', procurement.company_id.id)], limit=1,
            #                                            )
            #     if company_supplier:
            #         return supplierinfo.browse(company_supplier[0].id,).name
            #     elif procurement.product_id.seller_id:
            #         return procurement.product_id.seller_id
            #     else:
            #         return self.env.ref('linkloving_purchase.res_partner_exception_supplier')


class linkloving_product_product(models.Model):
    _inherit = 'product.template'

    def do_process(self, cr, uid, ids, context=None):
        purchase_order_line_obj = self.pool['purchase.order.line']
        order_line = purchase_order_line_obj.browse(cr, uid, context['active_id'])
        if order_line.product_id.seller_ids:
            order = order_line.order_id
            order.order_line -= order_line
            # order.order_line.remove(order_line)
        return {'type': 'ir.actions.act_window_close'}


class procurement_compute_all(osv.osv_memory):
    _inherit = 'procurement.order.compute.all'

    def _procure_calculation_all(self, cr, uid, ids, context=None):
        return super(procurement_compute_all, self)._procure_calculation_all(cr, uid, ids, context)

        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Modify Product',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'product.template',
        #     'view_id': self.env.ref('linkloving_purchase.modify_product_supplier').id,
        #     'res_id': self.product_id.product_tmpl_id.id,
        #     'target': 'new',
        # }

    def procure_calculation(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        self.get_scheduler_is_running()
        return super(procurement_compute_all, self).procure_calculation(cr, uid, ids, context)

    def get_scheduler_is_running(self):

        new_cr = self.pool.cursor()
        scheduler_cron_id = self.pool['ir.model.data'].get_object_reference(new_cr, SUPERUSER_ID, 'procurement',
                                                                            'ir_cron_scheduler_action')[1]
        # Avoid to run the scheduler multiple times in the same time
        try:
            with tools.mute_logger('openerp.sql_db'):
                new_cr.execute("SELECT id FROM ir_cron WHERE id = %s FOR UPDATE NOWAIT", (scheduler_cron_id,))
        except Exception:
            _logger.info('Attempt to run procurement scheduler aborted, as already running')
            new_cr.rollback()
            new_cr.close()
            raise osv.except_osv('Error!', 'Attempt to run procurement scheduler aborted, as already running')
            return {}
