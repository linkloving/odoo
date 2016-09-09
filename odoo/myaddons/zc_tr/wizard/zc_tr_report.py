# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 YDIT(www.chinamaker.net).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import osv, fields
from pprint import pprint
import datetime, calendar

class tr_print_report(osv.osv_memory):
	_name = 'tr.print.report'

	_columns = {
		'start_date': fields.date(u'订单开始日期'),
		'end_date': fields.date(u'订单截至日期'),
	}

	_defaults = {
		#'start_date': datetime.date(datetime.date.today().year,datetime.date.today().month,1),
		'start_date': (datetime.date.today().replace(day=1) - datetime.timedelta(1)).replace(day=1),
		'end_date': fields.datetime.now(),
	}
	
	def _get_data_by_sale_order(self, cr, uid, date1, date2, context=None):
		sale_pool = self.pool.get('sale.order')
		
		state_values = {
           'waiting_date': u'待处理',
           'progress': u'销售订单',
           'manual': u'待开票',
           'shiping_except': u'发货异常',
           'invoice_except': u'发票异常',
           'done': u'完成',
         }
         
		sale_ids = sale_pool.search(cr, uid, [('state', 'in', ['waiting_date', 'progress', 'manual', 'shipping_except', 'invoice_except', 'done']), 
			('date_order', '>=', date1), ('date_order', '<=', date2)], context=context)

		returnDict = {}
		for sale in sale_pool.browse(cr, uid, sale_ids, context=context):
			returnDict.update({sale.id: {}})
			
			shipstr = u"未发货"
			if sale.shipped:
			    shipstr = u"已发货"

			returnDict[sale.id].update({'vals': {
					'number': sale.name,
					'partner_ref': sale.partner_id.ref,
					'partner_name': sale.partner_id.name,
					'phone': sale.partner_id.phone,
					'partner_number': sale.client_order_ref,
					'amount_total': sale.amount_total,
					'state': state_values[sale.state],
					'date_order': sale.date_confirm,
					'create_date': sale.create_date,
					'contact_man': sale.partner_id.street2,
					
					'shipped': shipstr,
					'sales_man': sale.user_id.name,
				}})

			returnDict[sale.id].update({'line': {}})
			for line in sale.order_line:
				returnDict[sale.id]['line'].update({line.id: {
					'name': line.product_id.name,
					'quantity': line.product_uom_qty,
					'product_manager': line.product_id.product_manager.name,
					'categ_id': line.product_id.categ_id.name, 
				}})

		return returnDict

	def print_report(self, cr, uid, ids, context=None):
		for report in self.browse(cr, uid, ids, context=context):

			datas = self._get_data_by_sale_order(cr, uid, report.start_date, report.end_date, context=context)
			report_name = 'zc_tr.report_sale_order'

			return self.pool['report'].get_action(cr, uid, ids, report_name, data=datas, context=context)

class tr_print_report_financial(osv.osv_memory):
	_name = 'tr.print.report.financial'

	_columns = {
		'start_date': fields.date(u'订单开始日期'),
		'end_date': fields.date(u'订单截至日期'),
	}

	_defaults = {
		'start_date': (datetime.date.today().replace(day=1) - datetime.timedelta(1)).replace(day=1),
		'end_date': fields.datetime.now(),
	}
	
	def _get_data_by_sale_order(self, cr, uid, date1, date2, context=None):
		sale_pool = self.pool.get('sale.order')
		
		state_values = {
           'waiting_date': u'待处理',
           'progress': u'处理中',
           'manual': u'待开票',
           'shiping_except': u'发货异常',
           'invoice_except': u'发票异常',
           'done': u'完成',
         }
         
		sale_ids = sale_pool.search(cr, uid, [('state', 'in', ['waiting_date', 'progress', 'manual', 'shipping_except', 'invoice_except', 'done']), 
			('date_order', '>=', date1), ('date_order', '<=', date2)], context=context)

		returnDict = {}
		for sale in sale_pool.browse(cr, uid, sale_ids, context=context):
			returnDict.update({sale.id: {}})
			
			shipstr = u"未发货"
			if sale.shipped:
			    shipstr = u"已发货"

			returnDict[sale.id].update({'vals': {
					'number': sale.name,
					'partner_ref': sale.partner_id.ref,
					'partner_name': sale.partner_id.name,
					'phone': sale.partner_id.phone,
					'partner_number': sale.client_order_ref,
					'amount_total': sale.amount_total,
					'state': state_values[sale.state],
					'date_order': sale.date_confirm,
					'create_date': sale.create_date,
					'contact_man': sale.partner_id.street2,
					
					
					'sales_man': sale.user_id.name,
				}})

			returnDict[sale.id].update({'line': {}})
			for line in sale.order_line:
				returnDict[sale.id]['line'].update({line.id: {
					'name': line.product_id.name,
					'quantity': line.product_uom_qty,
					
					'product_manager': line.product_id.product_manager.name,
					'categ_id': line.product_id.categ_id.name, 
				}})

		return returnDict

	def print_report(self, cr, uid, ids, context=None):
		for report in self.browse(cr, uid, ids, context=context):

			datas = self._get_data_by_sale_order(cr, uid, report.start_date, report.end_date, context=context)
			report_name = 'zc_tr.report_financial'

			return self.pool['report'].get_action(cr, uid, ids, report_name, data=datas, context=context)

class tr_print_report_financial_move(osv.osv_memory):
	_name = 'tr.print.report.financial.move'

	_columns = {
		'start_date': fields.date(u'订单开始日期'),
		'end_date': fields.date(u'订单截至日期'),
	}

	_defaults = {
		'start_date': (datetime.date.today().replace(day=1) - datetime.timedelta(1)).replace(day=1),
		'end_date': fields.datetime.now(),
	}
	
	def _get_data_by_sale(self, cr, uid, date1, date2, context=None):
		returnDict = {}
		move_pool = self.pool.get('stock.move')
		move_ids = move_pool.search(cr, uid, [('state', '=', 'done'), ('date', '>=', date1), ('date', '<=', date2)], context=context)

		for move in move_pool.browse(cr, uid, move_ids, context=context):
			returnDict.update({move.id: {
					'product': move.product_id.name,
                    'default_code': move.product_id.default_code,
					'partner': move.picking_id.picking_type_id.code == 'outgoing' and move.partner_id.name or '',
					'supplier': move.picking_id.picking_type_id.code == 'incoming' and move.partner_id.name or '',
					'date_done': move.picking_id.date_done,
					'quantity': move.product_uom_qty,
					'price_unit': move.price_unit,
					'price': move.product_uom_qty * move.price_unit,
				}})

		return returnDict

	def print_report(self, cr, uid, ids, context=None):
		for report in self.browse(cr, uid, ids, context=context):

			datas = self._get_data_by_sale(cr, uid, report.start_date, report.end_date, context=context)
			report_name = 'zc_tr.report_financial_move'

			return self.pool['report'].get_action(cr, uid, ids, report_name, data=datas, context=context)

class tr_print_report_purchase(osv.osv_memory):
	_name = 'tr.print.report.purchase'

	_columns = {
		'start_date': fields.date(u'订单开始日期'),
		'end_date': fields.date(u'订单截至日期'),
	}

	_defaults = {
		'start_date': (datetime.date.today().replace(day=1) - datetime.timedelta(1)).replace(day=1),
		'end_date': fields.datetime.now(),
	}
	
	def _get_data_by_purchase(self, cr, uid, date1, date2, context=None):
		returnDict = {}
		purchase_pool = self.pool.get('purchase.order')
		purchase_line_pool = self.pool.get('purchase.order.line')
		move_pool = self.pool.get('stock.move')

		purchase_ids = purchase_pool.search(cr, uid, [('state', 'in', ['confirmed', 'approved', 'except_picking', 'except_invoice', 'done']), 
			('date_order', '>=', date1), ('date_order', '<=', date2)], order='name desc', context=context)

		purchase_sequence = 1
		for purchase in purchase_pool.browse(cr, uid, purchase_ids, context=context).sorted():

			delivery_price = 0
			forecast_price = 0
			print purchase.name
			for delivery in purchase.picking_ids:
				for d_line in delivery.move_lines:
					delivery_price += d_line.product_uom_qty * d_line.purchase_line_id.price_unit
					
			print 'delivery_price', delivery_price
			voucher_price = sum([sum([payment.debit for payment in invoice.payment_ids]) for invoice in purchase.invoice_ids])
			returnDict[purchase.id] = {'data': {}, 'line': {}}
			returnDict[purchase.id]['data'] = {
				'sequence': purchase_sequence,
				'name': purchase.name,
				'partner': purchase.partner_id.name,
				'user': purchase.validator.name,
				'date_order': purchase.date_order,
				'order_price': purchase.amount_total,
				'invoice_price': sum([invoice.amount_total for invoice in purchase.invoice_ids]),
				'voucher_price': voucher_price,
				'forecast_price': forecast_price,
				'delivery_price': delivery_price,
				'own_price': purchase.amount_total - voucher_price,
				'is_done': purchase.amount_total == voucher_price and u'是' or u'否',
			
			}

			for line in purchase.order_line:
				move_ids = move_pool.search(cr, uid, [('purchase_line_id', '=', line.id)], context=context)
				
				delivery_qty = forecast_qty = 0
				if move_ids:
					move = move_pool.browse(cr, uid, move_ids[0], context=context)
					delivery_qty = move.product_uom_qty
					
	
				returnDict[purchase.id]['line'].update({line.id: {
					'name': line.product_id.name,
					'category': line.product_id.categ_id.name,
					'default_code': line.product_id.default_code,
					
					'price_unit': line.price_unit,
					'quantity': line.product_qty,
					'forecast_qty': forecast_qty,
					'delivery_qty': delivery_qty,
					'order_price': line.price_unit * line.product_qty,
				}})

		return returnDict

	def print_report(self, cr, uid, ids, context=None):
		for report in self.browse(cr, uid, ids, context=context):

			datas = self._get_data_by_purchase(cr, uid, report.start_date, report.end_date, context=context)
			report_name = 'zc_tr.report_purchase'

			return self.pool['report'].get_action(cr, uid, ids, report_name, data=datas, context=context)

class tr_print_material_balance(osv.osv_memory):
	_name = 'tr.print.material.balance'

	def _get_period(self, cr, uid, context=None):
		ctx = dict(context or {})
		period_ids = self.pool.get('account.period').find(cr, uid, context=ctx)
		return period_ids[0]

	_columns = {
		'start_date': fields.date(u'订单开始日期'),
		'end_date': fields.date(u'订单截至日期'),
	}

	_defaults = {
		'start_date': (datetime.date.today().replace(day=1) - datetime.timedelta(1)).replace(day=1),
		'end_date': fields.datetime.now(),
		}
	
	def _get_data_by_material(self, cr, uid, date_start, date_end, context=None):
		
		res = []
		if date_end:
			cr.execute('''
					select product_id from stock_move m
						LEFT JOIN stock_picking s on (m.picking_id = s.id)
						LEFT JOIN stock_picking_type st on (s.picking_type_id = st.id)
						LEFT JOIN product_product p on (m.product_id = p.id)					

					where st.code in ('outgoing', 'incoming')
					GROUP BY product_id
				''')

			product_ids = cr.fetchall()

			for product_id in product_ids:
				cr.execute('''
					select sum(CASE WHEN st.code = 'outgoing' AND m.date >= %(date_start)r AND m.date <= %(date_end)r THEN m.product_uom_qty ELSE 0 END) as out_qty,
					       sum(CASE WHEN st.code = 'incoming' AND m.date >= %(date_start)r AND m.date <= %(date_end)r THEN m.product_uom_qty ELSE 0 END) as in_qty,
					       (sum(CASE WHEN st.code = 'incoming' AND m.date <= %(date_start)r THEN m.product_uom_qty ELSE 0 END) - 
					       	sum(CASE WHEN st.code = 'outgoing' AND m.date <= %(date_start)r THEN m.product_uom_qty ELSE 0 END)) as before_qty, 
					       (sum(CASE WHEN st.code = 'incoming' AND m.date <= %(date_end)r THEN m.product_uom_qty ELSE 0 END) - 
					       	sum(CASE WHEN st.code = 'outgoing' AND m.date <= %(date_end)r THEN m.product_uom_qty ELSE 0 END)) as after_qty,
						   p.default_code as default_code,
						   t.name as name,
						   pc.name as pc_name

					
					FROM stock_move m
					LEFT JOIN stock_picking s on (m.picking_id = s.id)
					LEFT JOIN stock_picking_type st on (s.picking_type_id = st.id)
					LEFT JOIN product_product p on (m.product_id = p.id)
						LEFT JOIN product_template t on (p.product_tmpl_id = t.id)
						LEFT JOIN product_category pc on (t.categ_id = pc.id)		

					WHERE st.code in ('outgoing', 'incoming') AND p.id = %(product_id)r
					GROUP BY p.default_code,
							 t.name,
							 pc.name
					''' % {'date_start': date_start, 'date_end': date_end, 'product_id': product_id[0]})

				res.append(cr.dictfetchall()[0])

		return res or []

	def print_report(self, cr, uid, ids, context=None):
		for report in self.browse(cr, uid, ids, context=context):
			datas = self._get_data_by_material(cr, uid, report.start_date, report.end_date, context=context)

			report_name = 'zc_tr.report_material'

			return self.pool['report'].get_action(cr, uid, ids, report_name, data=datas, context=context)

class tr_report_financial_purchase(osv.osv_memory):
	_name = 'tr.report.financial.purchase'

	_columns = {
		'start_date': fields.date(u'订单开始日期'),
		'end_date': fields.date(u'订单截至日期'),
	}

	_defaults = {
		'start_date': (datetime.date.today().replace(day=1) - datetime.timedelta(1)).replace(day=1),
		'end_date': fields.datetime.now(),
	}
	
	def _get_data_by_financial_purchase(self, cr, uid, start_date, end_date, context=None):
		order_obj = self.pool.get('purchase.order')
		line_obj = self.pool.get('purchase.order.line')

		res = []
		line_ids = line_obj.search(cr, uid, [
#				('order_id.state', '=', 'done'),
				('order_id.date_order', '>=', start_date),
				('order_id.date_order', '<=', end_date),
			], context=context)

		for line in line_obj.browse(cr, uid, line_ids, context=context):
			res.append({
					'order_ref': line.order_id.name,
					'partner_id': line.partner_id.name,
					'default_code': line.product_id.default_code,
					'categ_name': line.product_id.categ_id.name,
					'name': line.product_id.name,
					'product_uom': 'PCS',#line.product_id.uom_id.name,
					'product_uom_qty': line.product_qty,
					'price_unit': line.price_unit,
					'amount': line.product_qty * line.price_unit,
				})

		return res or []

	def print_report(self, cr, uid, ids, context=None):
		for report in self.browse(cr, uid, ids, context=context):
			datas = self._get_data_by_financial_purchase(cr, uid, report.start_date, report.end_date, context=context)

			report_name = 'zc_tr.report_financial_purchase'

			return self.pool['report'].get_action(cr, uid, ids, report_name, data=datas, context=context)

class tr_approve_wizard(osv.osv_memory):
	_name = 'tr.approve.wizard'

	def approved(self, cr, uid, ids, context=None):
		for approve in self.browse(cr, uid, ids, context=context):
			active_obj = self.pool.get(context.get('active_model'))

			if active_obj and context.get('active_id'):
				active_model = active_obj.browse(cr, uid, context.get('active_id'), context=context)
				old_state = active_model.state 
				if context.get('approve'):
					active_model.signal_workflow('approve')
				if context.get('reject'):
					active_model.signal_workflow('reject')
				active_model = active_obj.browse(cr, uid, context.get('active_id'), context=context)
				new_state  = active_model.state
				# Only log the approve history when approve done
				if old_state <> new_state:
					active_model.write({'approve_ids': [(0, 0, {
							'user_id': uid,
							'state': context.get('approve') and 'approve' or 'reject',
							'suggestion': approve.message
						})]})

	_columns = {
		'message': fields.char(u'审批意见'),
	}