# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class StockInvoiceShippingWizard(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    def open_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id')
        picking = self.pool['stock.picking'].browse(cr, uid, active_id, context=context)

        invoice_ids = self.create_invoice(cr, uid, ids, context=context)
        if not invoice_ids:
            raise osv.except_osv(_('Error!'), _('No invoice created!'))

        data = self.browse(cr, uid, ids[0], context=context)

        action_model = False
        action = {}

        journal2type = {'sale': 'out_invoice', 'purchase': 'in_invoice', 'sale_refund': 'out_refund',
                        'purchase_refund': 'in_refund'}
        inv_type = journal2type.get(data.journal_type) or 'out_invoice'
        data_pool = self.pool.get('ir.model.data')
        if inv_type == "out_invoice":
            action_id = data_pool.xmlid_to_res_id(cr, uid, 'account.action_invoice_tree1')
        elif inv_type == "in_invoice":
            action_id = data_pool.xmlid_to_res_id(cr, uid, 'account.action_invoice_tree2')
        elif inv_type == "out_refund":
            action_id = data_pool.xmlid_to_res_id(cr, uid, 'account.action_invoice_tree3')
        elif inv_type == "in_refund":
            action_id = data_pool.xmlid_to_res_id(cr, uid, 'account.action_invoice_tree4')

        if action_id:
            action_pool = self.pool['ir.actions.act_window']
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]"
            return action
        return True
