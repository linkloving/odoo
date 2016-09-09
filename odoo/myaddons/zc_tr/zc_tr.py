# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from pprint import pprint
from openerp import api
import datetime, calendar


class tr_approve(osv.osv):
    _name = 'tr.approve'

    _columns = {
        'approve_ids': fields.one2many('tr.approve.line', 'approve_id', u'审批'),
    }

class tr_approve_line(osv.osv):
    _name = 'tr.approve.line'

    _columns = {
        'approve_id': fields.many2one('tr.approve', u'审批'),
        'user_id': fields.many2one('res.users', u'审批人员'),
        'suggestion': fields.char(u'审批备注'),
        'state': fields.selection([('reject', u'拒绝'),('approve', u'同意')], u'审批状态'),
        'date': fields.datetime(u'时间'),
    }

    _defaults = {
        'date': fields.datetime.now,
    }

class tr_payment_budget(osv.Model):
    _name = 'tr.payment.budget'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherits = {'tr.approve': 'approve_id'} 
    _description = u'付款预算'
    _rec_name = 'period_id'

    def print_approve(self, cr, uid, ids, context=None):
        report_name = 'zc_tr.report_print_approve'
        return self.pool['report'].get_action(cr, uid, ids, report_name, context=context)

    def create_voucher(self, cr, uid, ids, context=None):
        #todo: 上月预算到当月5号之后作废，不能生成付款
        DATE_FORMAT = "%Y-%m-%d" 
        start_date_obj =(datetime.datetime.today().replace(day=1) - datetime.timedelta(1)).replace(day=1)
        start_date= datetime.datetime.strftime(start_date_obj, DATE_FORMAT) 
        print start_date
   
        now_date = datetime.datetime.strftime(datetime.date.today(), DATE_FORMAT)
        print now_date
        
        day5_obj = (datetime.datetime.today().replace(day=25) - datetime.timedelta(1)).replace(day=25)
        day5 = datetime.datetime.strftime(day5_obj, DATE_FORMAT)
        print day5 
        voucher_pool = self.pool.get('account.voucher')
       
        voucher_ids = []       
        for budget in self.browse(cr, uid, ids, context=context):
            invoices = {}
            for  line in budget.supplier_invoice_ids:
                #if line.create_date<start_date or now_date> day5:
                #    raise osv.except_osv(u'错误!',u'预算已经过期(上月预算次月25号后不能再生成付款)')
                voucher_id = voucher_pool.create(cr, uid, {'partner_id':line.partner_id.id,
                                                           'po':line.po.id,
                                                           'budget':budget.id,
                                                           'amount':line.amount,
                                                           'account_id':line.partner_id.property_account_payable.id,
                                                           'type':'payment'
                                                           }, context=context)
                voucher_ids.append(voucher_id)
                #将付款单号写入预算行
                #line.write({'voucher_id':voucher_id, 'voucher_id_str': voucher_id.name})
                line.write({'voucher_id':voucher_id})
                        
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return {
            'name': '供应商付款',
            'domain': [('id', 'in', voucher_ids)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'account.voucher',
            'type':'ir.actions.act_window',
            'context':context,
        }

    def onchange_period(self, cr, uid, ids, period_id, context=None):
        period_pool = self.pool.get('account.period')
        po_pool = self.pool.get('purchase.order')
        if not period_id:
            return {}
        period = period_pool.read(cr, uid, period_id, ['date_stop'], context=context)['date_stop']

        supplier_value = []
        if period:
            po_ids = po_pool.search(cr,uid,[],context=context)
            for po in po_pool.browse(cr,uid,po_ids,context=context):
                
                products = u'、'.join(set([line.product_id.categ_id.name for line in po.order_line]))
                project  = ''
                date_due = period[0:7]
                paid = 0.00
                incoming = 0.00
                amount = 0.00
                budget = 0.00
                month_paid = 0.00
 
                #当月 5号
                DATE_FORMAT = "%Y-%m-%d" 
                day5_obj = (datetime.datetime.today().replace(day=20) - datetime.timedelta(1)).replace(day=20)
                day5 = datetime.datetime.strftime(day5_obj, DATE_FORMAT)   
                #print day5
 
                #当前日期
                now_date = datetime.datetime.strftime(datetime.date.today(), DATE_FORMAT)
                #print now_date

                #实际付款
                #真实付款 从已经支付的凭证中读取
                voucher = self.pool.get('account.voucher')
                voucher_line_ids = voucher.search(cr,uid,[('po','=',po.id),('state', '<>', 'cancel')],context=context)
                for voucher_line in voucher.browse(cr,uid,voucher_line_ids,context=context):
                    paid += voucher_line.amount       # 已付款 
                #print paid


                #print u"计算到今天的预算"
                
                start_date_obj =(datetime.datetime.today().replace(day=1) - datetime.timedelta(1)).replace(day=1)
                start_date= datetime.datetime.strftime(start_date_obj, DATE_FORMAT) 
                #print start_date
                end_date= fields.datetime.now() 
                
                budget_line = self.pool.get('tr.supplier.account.invoice')
                line_ids = budget_line.search(cr,uid,[('po','=',po.id)],context=context)
                for line in budget_line.browse(cr,uid,line_ids,context=context):
                    budget += line.amount       # 已预算

                due_date = None	
                for pick in po.picking_ids:
                    if pick.state == 'done':
                        if po.payment_term_id:
                            pterm = self.pool['account.payment.term'].browse(cr,uid,po.payment_term_id.id,context=context)
                            pterm_list = pterm.compute(value=1, date_ref=pick.date_done[0:10])[0]
                            if pterm_list:
                                due_date = max(line[0] for line in pterm_list)
                        #else:
                            #due_date = pick.date_done
                        if due_date and due_date < period:
                            for move in pick.move_lines: 
                                amount += move.price_unit * move.product_uom_qty     # 到期日在本期间末之前
                            #print 'amount',amount
                    else:
                        if pick.state <> 'cancel':                                    # 取消的不计算
                            for move in pick.move_lines:
                                incoming += move.price_unit * move.product_uom_qty   # 未交货

                amount = round(amount, 2) - round(budget, 2)        # 当月到期
                if amount > 0.00:
                    #print products + po.name   
                    supplier_value.append((0, False, {'po': po.id,
                                                  'partner_id':po.partner_id.id,
                                                  'products':products,
                                                  'project':project,
                                                  'date_due':date_due,
                                                  'po_amount':po.amount_total,
                                                  'paid':paid,
                                                  'po_due':po.amount_total - paid,
                                                  'in_due':po.amount_total - incoming - paid,
                                                  'incoming':incoming,
                                                  'period_due':amount,
                                                  'amount':amount                              
                                                  }))  

        return {'value': {'supplier_invoice_ids': supplier_value}}
    def _get_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for budget in self.browse(cr,uid,ids,context=context):
            tot = 0.0
            for line in budget.supplier_invoice_ids:
                tot += line.amount
            res.update({budget.id:tot})
        return res 
    _columns = {
        'name' : fields.char(u'预算付款单', required=True, select=True, copy=False,
                            help="Unique number of the budget order, "
                                 "computed automatically when the budget order is created."),
        'period_id': fields.many2one('account.period', u'会计期间'),
        'supplier_invoice_ids': fields.one2many('tr.supplier.account.invoice', 'budget_id', 
                                                u'付款预算行'),
        'approve_id': fields.many2one('tr.approve', u'审批', required=True, ondelete='cascade', select=True, auto_join=True),
        'state': fields.selection([
            ('draft','草稿'),
            ('submited',u'已提交审核'),
            ('1st',u'一级审核通过'),
            ('2nd',u'二级审核通过'),
            ('3rd',u'三级审核通过'),
            ('4th',u'全部审核通过'),
            ('done', u'已生成付款'),
        ], string=u'状态', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False),
        'amount':fields.function(_get_total,type='float',string=u'合计',store=True),
    }
    _defaults = {
        'state': 'draft',
        'name': lambda obj, cr, uid, context: '/',
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'payment.budget.order', context=context) or '/'
        context = dict(context or {}, mail_create_nolog=True)
        order =  super(tr_payment_budget, self).create(cr, uid, vals, context=context)
        self.message_post(cr, uid, [order], body=_("payment budget order created"), context=context)
        return order
    
    @api.multi
    def unlink(self):
        for budget in self:
            if budget.state not in ('draft'):
                raise osv.except_osv(u'错误!',u'不能删除非草稿状态的预算！！！')
        return super(tr_payment_budget, self).unlink()

class tr_supplier_account_invoice(osv.Model):
    _name = 'tr.supplier.account.invoice'
    _order = 'po desc'

    def onchange_amount(self,cr,uid,ids,new_amt,context=None):
        res = {}
        for old in self.browse(cr,uid,ids,context=context):
            if old.amount > 0 and new_amt > old.amount:
                res.update({'value':{'amount':old.amount},
                            'warning':{'title':'错误', 'message':'申请金额不能大于合同金额！'}
                            })
        return res
    
    def onchange_po(self, cr, uid, ids, po_id, context=None):
        po_value = {}   
        paid = 0.00
        budget = 0.00
        print po_id
        if not po_id:
            return {'value': {'po': False, 'partner_id': False,  'po_amount': False}}
        
        po_pool = self.pool.get('purchase.order')
       
        po = po_pool.browse(cr, uid, po_id, context=context)

        products = u'、'.join(set([line.name for line in po.order_line]))
        print po
        if po:
            #实际付款
            #真实付款 从已经支付的凭证中读取
            voucher = self.pool.get('account.voucher')
            voucher_line_ids = voucher.search(cr,uid,[('po','=',po.id),('state', '<>', 'cancel')],context=context)
            for voucher_line in voucher.browse(cr,uid,voucher_line_ids,context=context):
                paid += voucher_line.amount       # 已付款 
            print paid
            budget_line = self.pool.get('tr.supplier.account.invoice')
            line_ids = budget_line.search(cr,uid,[('po','=',po.id)],context=context)
            for line in budget_line.browse(cr,uid,line_ids,context=context):
                budget += line.amount       # 已预算
            po_value.update({'po': po.id,
                                    'partner_id': po.partner_id.id,
                                    'po_amount': po.amount_total, 
                                    'products': products,                          
                                    'paid':paid,
                                    #'po_due':po.amount_total - budget,
                                    'po_due':po.amount_total - paid,
                                                  })  
        #return {'value': po_value}
        #return {'value': {'supplier_invoice_ids': po_value}}
        #return po_value
        print po_value
        return {'value': po_value}	
    _columns = {
        'budget_id': fields.many2one('tr.payment.budget', u'付款预算',ondelete='cascade'),
        'po':fields.many2one('purchase.order',string=u'合同号'),
        'partner_id': fields.many2one('res.partner', string=u'供应商'),
        'products':fields.char(u'产品名称'),
        'project':fields.char(u'项目'),
        'date_due':fields.char(u'付款月份'),
        'po_amount':fields.float(u'合同金额'),
        'paid':fields.float(u'累计支付'),
        'po_due':fields.float(u'欠款'),
        'in_due':fields.float(u'待定欠款'),
        'incoming':fields.float(u'待执行金额'),
        'period_due':fields.float(u'当月到期金额'),
        'amount': fields.float(string=u'即期支票电汇'),
        'reason': fields.char(string=u'备注'),
        'voucher_id':fields.many2one('account.voucher',u'付款单号'),
        #'voucher_id_str':fields.char(u'付款单号'),
    }

class account_invoice(osv.Model):
    _inherit = 'account.invoice'
    _inherits = {'tr.approve': 'approve_id'}

    def print_approve(self, cr, uid, ids, context=None):
        report_name = 'zc_tr.report_print_approve_invoice'
        return self.pool['report'].get_action(cr, uid, ids, report_name, context=context)
    
    def _get_data_by_invoice(self, cr, uid, invoice, context=None):
        # 销售发票都是基于订单生成的
        sale_order = None
        order_id = self.pool.get('sale.order').search(cr, uid, [('name','=',invoice.origin)],context=context)
        if order_id:
            sale_order = self.pool.get('sale.order').browse(cr, uid, order_id, context=context)
        vals = {
            'header': {
                'sale_number':sale_order and sale_order.name or '',
                'sale_total':sale_order and sale_order.amount_total or 0.0,
                'project':sale_order and sale_order.client_order_ref or '',
                'customer_name': invoice.partner_id.name,
                'customer_vat':invoice.partner_id.vat or '',
                'customer_add':(invoice.partner_id.street or '') + (invoice.partner_id.phone or ''),
                'customer_bank': (invoice.partner_id.bank_ids[0].bank_name + invoice.partner_id.bank_ids[0].acc_number) if invoice.partner_id.bank_ids else '',
                'category':invoice.tr_invoice_category,
                'contact':invoice.tr_invoice_contact,
                'phone':invoice.tr_invoice_phone,
                'post':invoice.tr_invoice_post,
                'add':invoice.tr_invoice_add,
            },
            'line':[]
        }

        sequence = 1
        for line in invoice.invoice_line:
            vals['line'].append({
                    'category': line.product_id.name,
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'price_subtotal':line.price_subtotal,
                })
        return vals

    def print_report(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context=context):
            datas = self._get_data_by_invoice(cr, uid, invoice, context=context)
            report_name = 'zc_tr.report_out_invoice'
            return self.pool['report'].get_action(cr, uid, ids, report_name, data=datas, context=context)
        
    def _get_po(self, cr, uid, ids, field_name, arg, context=None):
        pick_obj = self.pool.get('stock.picking')
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            res[inv.id] = {
                           'tr_po_number':None,
                           'tr_po_total':0.0,
                           }
            #TODO logic of fill them
            if inv.origin:
                pick_id = pick_obj.search(cr,uid,[('name','=',inv.origin)])
                if pick_id:
                    tr_po = pick_obj.read(cr,uid,pick_id,['origin'])[0]['origin']
                    if tr_po:
                        po_id = self.pool.get('purchase.order').search(cr,uid,[('name','=',tr_po)])
                        po = self.pool.get('purchase.order').browse(cr,uid,po_id)
                        res[inv.id]['tr_po_number'] = po.id
                        res[inv.id]['tr_po_total'] = po.amount_total
        return res
 
    def _get_paid(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            res[inv.id] = {
                           'tr_po_paid':0.0,
                           'tr_po_rem':0.0,
                           }
            if inv.tr_po_number:
                #真实付款 从已经支付的凭证中读取
                paid = 0.00
                voucher = self.pool.get('account.voucher')
                voucher_line_ids = voucher.search(cr,uid,[('po','=',inv.tr_po_number.id),('state', '<>', 'draft'),('state', '<>', 'cancel')],context=context)
                for voucher_line in voucher.browse(cr,uid,voucher_line_ids,context=context):
                    paid += voucher_line.amount       # 已付款 
                res[inv.id]['tr_po_paid'] = paid

                all_invoice = self.search(cr,uid,[('tr_po_number','=',inv.tr_po_number.id)],context=context)
                if all_invoice:
                    for invoice in self.browse(cr,uid,all_invoice,context=context):
                        if inv.id != invoice.id:
                            #res[inv.id]['tr_po_paid'] += (invoice.amount_total - invoice.residual)
                            res[inv.id]['tr_po_rem'] += invoice.amount_total
        return res
     
    _columns = {
        'state': fields.selection([
            ('draft','Draft'),
            ('submited',u'已提交审核'),
            ('1st',u'一级审核通过'),
            ('2nd',u'二级审核通过'),
            ('3rd',u'三级审核通过'),
            ('4th',u'全部审核通过'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' when invoice is in Pro-forma status,invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice."),
        'approve_id': fields.many2one('tr.approve', u'审批', required=True, ondelete='cascade', select=True, auto_join=True),
# 客户要求将采购发票改为材料采购报销单
        'tr_invoice_type':fields.char(u'发票类型'),
        'tr_expense_type':fields.char(u'报销类型'),
        'tr_department':fields.char(u'报销部门'),
        'tr_po_number':fields.function(_get_po,type='many2one',relation='purchase.order',string=u'合同编号',multi='po',store=True),
        'tr_po_total':fields.function(_get_po,tye='float',string=u'合同金额',multi='po'),
        'tr_po_paid':fields.function(_get_paid,tye='float',string=u'已付款',multi='paid'),
        'tr_po_rem':fields.function(_get_paid,tye='float',string=u'已报销金额',multi='paid'), # 已经开发票还没有付款的？
        'tr_usage':fields.char(u'材料用途'),
# 客户要求将销售发票改发票申请单
        'tr_invoice_category':fields.selection([('c1',u'增值税普票'),('c2',u'增值税专票'),('c3',u'营改增普票'),('c4',u'营改增专票'),('c5',u'服务业发票'),('c6',u'收据')], string=u'发票类别'),
        'tr_invoice_contact':fields.char(u'收件人'),
        'tr_invoice_phone':fields.char(u'电话'),
        'tr_invoice_post':fields.char(u'邮编'),
        'tr_invoice_add':fields.char(u'地址'),
    }
    
    _defaults = {
        'tr_invoice_type': u'增值税发票',
        'tr_expense_type': u'不支取款项',
        'tr_department': u'采购部',
        'tr_usage':u'通用材料' 
    }

    @api.multi
    def unlink(self):
        for invoice in self:
            if invoice.state not in ('draft', 'cancel'):
                raise Warning(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
            elif invoice.internal_number:
                raise Warning(_('You cannot delete an invoice after it has been validated (and received a number).  You can set it back to "Draft" state and modify its content, then re-confirm it.'))
        
        #pick_obj = self.pool.get('stock.picking')
        #pick_id = pick_obj.search(cr, uid , [('name','=',self.origin)])
        pick_id = self.env['stock.picking'].search([('name','=',self.origin)])
        print self.origin
        print pick_id
        if pick_id:
            pick_id.write({'invoice_state': '2binvoiced'})   
            for move in pick_id.move_lines:
                move.write({'invoice_state':'2binvoiced'}) 
        return super(account_invoice, self).unlink()
    

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    _columns = {
        'categ_id': fields.related('product_id', 'categ_id', type='many2one', relation='product.category', string=u'分类', readonly='1'),
    }
    


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _inherits = {'tr.approve': 'approve_id'}

    def print_approve(self, cr, uid, ids, context=None):
        report_name = 'zc_tr.report_print_approve_voucher'
        return self.pool['report'].get_action(cr, uid, ids, report_name, context=context)

    _columns = {
        'state':fields.selection(
            [('draft','Draft'),
             ('submited',u'已提交审核'),
             ('1st',u'一级审核通过'),
             ('2nd',u'二级审核通过'),
             ('3rd',u'三级审核通过'),
             ('4th',u'全部审核通过'),
             ('cancel','Cancelled'),
             ('proforma','Pro-forma'),
             ('posted','Posted')
            ], 'Status', readonly=True, track_visibility='onchange', copy=False,
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                        \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Cancelled\' status is used when user cancel voucher.'),
        'budget': fields.many2one('tr.payment.budget', u'付款预算'),
        'po':fields.many2one('purchase.order',string=u'合同号'),
        'end_date':fields.date(u'票据到期日',help=u'银行承兑汇票或者商业承兑汇票的到期日'),
        'approve_id': fields.many2one('tr.approve', u'审批', required=True, ondelete='cascade', select=True, auto_join=True),
        'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=False, states={'posted':[('readonly',True)]}),
    }


