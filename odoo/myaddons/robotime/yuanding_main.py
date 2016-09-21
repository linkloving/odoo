# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import models, fields
from openerp.osv import fields as fieldsold
from openerp.tools.translate import _
from openerp.tools import float_compare

class stock_picking(osv.Model):
    _inherit = 'stock.picking'
class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {        
        'product_sepcs': fieldsold.related('product_id', 'product_sepcs', string=u'材料编码', type='char', readonly='1'),
    }       
class feiyType(models.Model):
    _name = 'hr.expense.expense.type'

    name = fields.Char(string=u'费用科目', translate=True)
class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    def _get_recieve_amount(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for po in self.browse(cursor, user, ids, context=context):
            #if purc.invoiced:
            #    res[purc.id] = '100%'
            #    continue
            tot = 0
            for pick in  po.picking_ids:
                    if pick.state == 'done':
                        
                        for move in pick.move_lines: 
                            tot += move.product_uom_qty     # 到期日在本期间末之前
            if tot:
                res[po.id] = tot           
            else:
                res[po.id] = 0
        return res
    
    _columns={   
            'receive_amount': fieldsold.function(_get_recieve_amount, string=u'已收数量', type='float'),    
            }    
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
        ''' prepare the stock move data from the PO line. This function returns a list of dictionary ready to be used in stock.move's create()'''
        product_uom = self.pool.get('product.uom')
        price_unit = order_line.price_unit
        '''
        if order_line.taxes_id:
            taxes = self.pool['account.tax'].compute_all(cr, uid, order_line.taxes_id, price_unit, 1.0,
                                                             order_line.product_id, order.partner_id)
            price_unit = taxes['total']
        '''
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
        res = []
        if order.location_id.usage == 'customer':
            name = order_line.product_id.with_context(dict(context or {}, lang=order.dest_address_id.lang)).name
        else:
            name = order_line.name or ''
        move_template = {
            'name': name,
            'product_id': order_line.product_id.id,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': order.date_order,
            'date_expected': fieldsold.date.date_to_datetime(self, cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id,
            'move_dest_id': False,
            'state': 'draft',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': order.picking_type_id.id,
            'group_id': group_id,
            'procurement_id': False,
            'origin': order.name,
            'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id':order.picking_type_id.warehouse_id.id,
            'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
        }

        diff_quantity = order_line.product_qty
        for procurement in order_line.procurement_ids:
            procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=order_line.product_uom.id)
            tmp = move_template.copy()
            tmp.update({
                'product_uom_qty': min(procurement_qty, diff_quantity),
                'product_uos_qty': min(procurement_qty, diff_quantity),
                'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
                'procurement_id': procurement.id,
                'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state=='2binvoiced' and '2binvoiced') or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
                'propagate': procurement.rule_id.propagate,
            })
            diff_quantity -= min(procurement_qty, diff_quantity)
            res.append(tmp)
        #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
        #split the future stock move in two because the route followed may be different.
        if float_compare(diff_quantity, 0.0, precision_rounding=order_line.product_uom.rounding) > 0:
            move_template['product_uom_qty'] = diff_quantity
            move_template['product_uos_qty'] = diff_quantity
            res.append(move_template)
        return res

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'product_sepcs': fieldsold.related('product_id', 'product_sepcs', string=u'材料编码', type='char', readonly='1'),
        'product_id': fieldsold.many2one('product.product', 'Product', domain=[('purchase_ok','=',True)], change_default=True,required=True,
                                           states={'draft': [('readonly', False)]})
               }
class stock_picking(osv.Model):
    _inherit = 'stock.picking'

    _columns = {
        'validate_state': fieldsold.selection([
            ('draft', '未提交审核'),
            ('submited',u'已提交审核'),
            ('1th',u'质检审核通过'),
            ], 'Status', readonly=True, copy=False, track_visibility='onchange',select=True), 
    }    
class hr_expense_expense(osv.osv):
   
    _inherit = 'hr.expense.expense'
    _columns = {
        'order_type': fieldsold.many2one('hr.expense.expense.type', string=u'费用科目', required=True),
	    'code': fieldsold.char(u'报销编号'),
		}							   
    _defaults = {
      
        'code': lambda self, cr, uid, context=None: '/',
       
    }							   
								   
    def default_get(self, cr, uid, fields, context=None):
        context = context or {}
        res = super(hr_expense_expense, self).default_get(cr, uid, fields, context=context)
        newcode = self.pool.get('ir.sequence').get(cr, uid, 'ydit.box.number') or '/' 
        res.update(code=newcode)
        return res	
#投料不允许负库存        
class stock_move_consume(osv.osv_memory):
    _inherit = "stock.move.consume"
    def do_move_consume(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        production_obj = self.pool.get('mrp.production')
        move_ids = context['active_ids']
        move = move_obj.browse(cr, uid, move_ids[0], context=context)
        production_id = move.raw_material_production_id.id
        production = production_obj.browse(cr, uid, production_id, context=context)
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')

        for data in self.browse(cr, uid, ids, context=context):
            qty = uom_obj._compute_qty(cr, uid, data['product_uom'].id, data.product_qty, data.product_id.uom_id.id)
            if qty > data.product_id.qty_available:
                raise osv.except_osv(_(u'错误!'), _(u'需要移动数量大于库存数量,产品: \'%s\'.') % data.product_id.name)
            remaining_qty = move.product_qty - qty
            #check for product quantity is less than previously planned
            if float_compare(remaining_qty, 0, precision_digits=precision) >= 0:
                move_obj.action_consume(cr, uid, move_ids, qty, data.location_id.id, restrict_lot_id=data.restrict_lot_id.id, context=context)
            else:
                consumed_qty = min(move.product_qty, qty)
                new_moves = move_obj.action_consume(cr, uid, move_ids, consumed_qty, data.location_id.id, restrict_lot_id=data.restrict_lot_id.id, context=context)
                #consumed more in wizard than previously planned
                extra_more_qty = qty - consumed_qty
                #create new line for a remaining qty of the product
                extra_move_id = production_obj._make_consume_line_from_data(cr, uid, production, data.product_id, data.product_id.uom_id.id, extra_more_qty, False, 0, context=context)
                move_obj.write(cr, uid, [extra_move_id], {'restrict_lot_id': data.restrict_lot_id.id}, context=context)
                move_obj.action_done(cr, uid, [extra_move_id], context=context)

        return {'type': 'ir.actions.act_window_close'}

class account_move(osv.osv):
    _inherit = 'account.move'
    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)
        if not valid_moves:
            raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name =='/':
                new_name = False
                journal = move.journal_id
                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                        new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                    else:
                        raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
                if new_name:
                    self.write(cr, uid, [move.id], {'name':new_name})
        cr.execute('UPDATE account_move '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))
        cr.execute('UPDATE hr_expense_expense '\
                   'SET state=%s '\
                   'WHERE account_move_id IN %s',
                   ('paid', tuple(valid_moves),))
        self.invalidate_cache(cr, uid, ['state', ], valid_moves, context=context)
        return True
