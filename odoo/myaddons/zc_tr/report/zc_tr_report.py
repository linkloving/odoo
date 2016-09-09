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

from openerp import http, tools
from openerp.http import request
from openerp.osv import osv, fields
from openerp.report import report_sxw
import simplejson
from datetime import datetime
import xlwt
import StringIO
from pprint import pprint

class report_sale_order(http.Controller):
    @http.route(['/report/zc_tr.report_sale_order'], type='http', auth='user', multilang=True)
    def report_sale_order(self, **data):
        data = simplejson.loads(data['options'])
        pprint(data)
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook()
            data_sheet = xls_wookbook.add_sheet('data')

            style = xlwt.easyxf(
                'align: vertical center, horizontal center;'
                'borders: left thin,, right thin,, top thin,, bottom thin,;'
                'font: height 250;'
                )

            header_style = xlwt.easyxf(
                'borders: left thin,, right thin,, top thin,, bottom thin,;'
                'align: vertical center, horizontal center;'
                'font: height 250, bold True;'
                )

            header_list = [u'合同编号', u'联系人' , u'客户名称', u'联系电话', u'订单产品', u'产品型号', 
                           u'订单数量', u'销售经理',
                           u'订单金额', u'合同状态',
                            u'合同签订日期', u'订单下单日期']
            [data_sheet.write(0, row, line, header_style) for row, line in enumerate(header_list)]

            row = 1
            for sale_id, sale_vals in data.iteritems():
                vals = sale_vals.get('vals')
                data_sheet.write(row, 0, vals.get('number') and vals.get('number') or '', style)
                data_sheet.write(row, 1, vals.get('contact_man')and vals.get('contact_man') or '', style)
                data_sheet.write(row, 2, vals.get('partner_name')and vals.get('partner_name') or '', style)
                data_sheet.write(row, 3, vals.get('phone')and vals.get('phone') or '', style)
                #data_sheet.write(row, 9, vals.get('partenr_number')and vals.get('partenr_number') or '', style)
                data_sheet.write(row, 10-2, vals.get('amount_total')and vals.get('amount_total') or 0, style)
                data_sheet.write(row, 11-2, vals.get('state')and vals.get('state') or '', style)
                data_sheet.write(row, 13-2, vals.get('date_order')and vals.get('date_order') or '', style)
                data_sheet.write(row, 12-2, vals.get('create_date')and vals.get('create_date') or '', style)
               
                data_sheet.write(row, 7, vals.get('sales_man') and vals.get('sales_man') or '', style)
                if not sale_vals.get('line'):
                    row += 1
                    continue

                for line_id, line in sale_vals.get('line').iteritems():
                    data_sheet.write(row, 4, line.get('name') and line.get('name') or '', style)
                    data_sheet.write(row, 5, line.get('categ_id') and line.get('categ_id') or '', style)
                    data_sheet.write(row, 6, line.get('quantity') and line.get('quantity') or '', style)

                    #data_sheet.write(row, 8, line.get('product_manager') and line.get('product_manager') or '', style)

                    row += 1

            for x, i in enumerate([2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]):
                data_sheet.col(x).width = 2560 * i

            for x in range(0, row):
                data_sheet.row(x).height_mismatch = 1
                data_sheet.row(x).height = 500

            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=salesum.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'该截至日期之前不存在销售订单')
'''
class report_protocol(http.Controller):
    @http.route(['/report/zc_tr.report_protocol'], type='http', auth='user', multilang=True)
    def report_protocol(self, **data):
        data = simplejson.loads(data['options'])
        pprint(data)
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook(encoding='utf-8')
            data_sheet = xls_wookbook.add_sheet('data')

            style = xlwt.easyxf(
                'font: height 250;'
                'align: vertical center, horizontal center;'
                'borders: left thin,, right thin,, top thin,, bottom thin,;'
                )

            header_style = xlwt.easyxf(
                'font: height 250, bold True;'
                'align: vertical center, horizontal center;'
                'borders: left thin,, right thin,, top thin,, bottom thin,;'
                )
            header_list = [
                u'协议编号', #u'客户编号', 
                u'客户名称', u'产品',
                u'型号', u'数量', #u'涉及金额', 
                u'销售经理', u'订单状态', #u'项目编号', 
                u'立项日期', u'下单日期', u'发货日期', u'结项日期', u'退库日期', #u'借货协议',
                u'发货状态', u'销售单号',
            ]

            [data_sheet.write(0, row, line, header_style) for row, line in enumerate(header_list)]

            row = 1
            for sale_vals in data.itervalues():
                vals = sale_vals.get('vals')
                data_sheet.write(row, 0, vals.get('name') and vals.get('name') or '', style)
                #data_sheet.write(row, 1, vals.get('city') and vals.get('city') or '', style)
                #data_sheet.write(row, 2, vals.get('state') and vals.get('state') or '', style)
                #data_sheet.write(row, 3, vals.get('partner_ref') and vals.get('partner_ref') or '', style)
                data_sheet.write(row, 4-3, vals.get('partner_name') and vals.get('partner_name') or '', style)
                data_sheet.write(row, 10-4, vals.get('state') and vals.get('state') or 0, style)
                #data_sheet.write(row, 11, vals.get('out_name') and vals.get('out_name') or '', style)
                data_sheet.write(row, 12-5, vals.get('protocol_date') and vals.get('protocol_date') or '', style)
                data_sheet.write(row, 13-5, vals.get('out_date') and vals.get('out_date') or '', style)
                data_sheet.write(row, 14-5, vals.get('out_date_done') and vals.get('out_date_done') or '', style)
                data_sheet.write(row, 15-5, vals.get('protocol_end_date') and vals.get('protocol_end_date') or '', style)
                data_sheet.write(row, 16-5, vals.get('protocol_return_date') and vals.get('protocol_return_date') or '', style)
                #data_sheet.write(row, 17, vals.get('protocol_return_name') and vals.get('protocol_return_name') or '', style)
                data_sheet.write(row, 18-6, vals.get('picking_state') and vals.get('picking_state') or '', style)
                data_sheet.write(row, 19-6, vals.get('order') and vals.get('order') or '', style)
                data_sheet.write(row, 9-4, vals.get('sale_manager') and vals.get('sale_manager') or '', style)
                if not sale_vals.get('line'):
                    row += 1
                    continue

                for line in sale_vals.get('line').itervalues():
                    data_sheet.write(row, 5-3, line.get('name') and line.get('name') or '', style)
                    #data_sheet.write(row, 6-3, line.get('specification') and line.get('specification') or '', style)
                    data_sheet.write(row, 6-3, line.get('categ_id') and line.get('categ_id') or '', style)
                    data_sheet.write(row, 7-3, line.get('quantity') and line.get('quantity') or '', style)
                    #data_sheet.write(row, 8-2, line.get('price') and line.get('price') or '', style)
                    

                    row += 1

            for x, i in enumerate([3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]):
                data_sheet.col(x).width = 2560 * i

            for x in range(0, row):
                data_sheet.row(x).height_mismatch = 1
                data_sheet.row(x).height = 500

            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=testsum.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'该截至日期之前不存在测试订单')
'''
class report_financial(http.Controller):
    @http.route(['/report/zc_tr.report_financial'], type='http', auth='user', multilang=True)
    def report_financial(self, **data):
        data = simplejson.loads(data['options'])
        pprint(data)
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook()
            data_sheet = xls_wookbook.add_sheet('data')

            style = xlwt.easyxf(
                'align: vertical center, horizontal center;'
                'borders: left thin,, right thin,, top thin,, bottom thin,;'
                'font: height 250;'
                )

            header_style = xlwt.easyxf(
                'borders: left thin,, right thin,, top thin,, bottom thin,;'
                'align: vertical center, horizontal center;'
                'font: height 250, bold True;'
                )

            header_list =  [u'所属年度',
                           u'合同编号', #u'联系人' ,
                           u'合同日期',   
                           u'客户名称', #u'联系电话',
                           u'订单产品', u'产品型号', 
                           u'订单数量', u'业务员',
                           u'订单金额', #u'合同状态',
                           #u'合同签订日期',
                          
                          ] #u'发货状态']
            [data_sheet.write(0, row, line, header_style) for row, line in enumerate(header_list)]

            row = 1
            for sale_id, sale_vals in data.iteritems():
                vals = sale_vals.get('vals')
                data_sheet.write(row, 1, vals.get('number') and vals.get('number') or '', style)
                #data_sheet.write(row, 1, vals.get('contact_man')and vals.get('contact_man') or '', style)
                data_sheet.write(row, 3, vals.get('partner_name')and vals.get('partner_name') or '', style)
                #data_sheet.write(row, 3, vals.get('phone')and vals.get('phone') or '', style)
                #data_sheet.write(row, 9, vals.get('partenr_number')and vals.get('partenr_number') or '', style)
                data_sheet.write(row, 8, vals.get('amount_total')and vals.get('amount_total') or 0, style)
                #data_sheet.write(row, 11-4, vals.get('state')and vals.get('state') or '', style)
                data_sheet.write(row, 2, vals.get('date_order') and vals.get('date_order') or '', style)
                data_sheet.write(row, 0, vals.get('create_date')[0:4]and vals.get('create_date')[0:4] or '', style)
                    #data_sheet.write(row, 16-5, vals.get('shipped')and vals.get('shipped') or '', style)
                data_sheet.write(row, 7, vals.get('sales_man') and vals.get('sales_man') or '', style)
                if not sale_vals.get('line'):
                    row += 1
                    continue

                for line_id, line in sale_vals.get('line').iteritems():
                    data_sheet.write(row, 4, line.get('name') and line.get('name') or '', style)
                    data_sheet.write(row, 5, line.get('categ_id') and line.get('categ_id') or '', style)
                    data_sheet.write(row, 6, line.get('quantity') and line.get('quantity') or '', style)

                    #data_sheet.write(row, 8, line.get('product_manager') and line.get('product_manager') or '', style)

                    row += 1

            for x, i in enumerate([2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]):
                data_sheet.col(x).width = 2560 * i

            for x in range(0, row):
                data_sheet.row(x).height_mismatch = 1
                data_sheet.row(x).height = 500

            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=salesum.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'该截至日期之前不存在销售订单')

class report_financial_move(http.Controller):
    @http.route(['/report/zc_tr.report_financial_move'], type='http', auth='user', multilang=True)
    def report_financial_move(self, **data):
        data = simplejson.loads(data['options'])
        pprint(data)
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook()
            data_sheet = xls_wookbook.add_sheet('data')

            style = xlwt.easyxf(
                'font: height 250;'
                'align: vertical center, horizontal center;'
                'borders: left thin,, right thin,, top thin,, bottom thin,;'
                )

            header_style = xlwt.easyxf(
                'borders: left thin,, right thin,, top thin,, bottom thin,;'
                'font: height 250, bold True;'
                'align: vertical center, horizontal center;'
                )
            
            header_list = [u'料号',u'产品',  u'客户', u'供应商', u'出入库日期', u'数量', u'单价', u'金额']
            [data_sheet.write(0, row, line, style) for row, line in enumerate(header_list)]
            for row, line in enumerate(data.itervalues()):
                data_sheet.write(row + 1, 0, line.get('default_code') and line.get('default_code') or '', style)
                data_sheet.write(row + 1, 0 + 1, line.get('product') and line.get('product') or '', style)
                data_sheet.write(row + 1, 1 + 1, line.get('partner') and line.get('partner') or '', style)
                data_sheet.write(row + 1, 2 + 1, line.get('supplier') and line.get('supplier') or '', style)
                data_sheet.write(row + 1, 3 + 1, line.get('date_done') and line.get('date_done').split(' ')[0] or '', style)
                data_sheet.write(row + 1, 4 + 1, line.get('quantity') and line.get('quantity') or 0, style)
                data_sheet.write(row + 1, 5 + 1, line.get('price_unit') and line.get('price_unit') or 0, style)
                data_sheet.write(row + 1, 6 + 1, line.get('price') and line.get('price') or 0, style)

            for x, i in enumerate([3, 3, 2, 2, 3, 1, 2]):
                data_sheet.col(x).width = 2560 * i

            for x in range(0, row):
                data_sheet.row(x).height_mismatch = 1
                data_sheet.row(x).height = 500

            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=stockmovesum.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'该截至日期之前不存在使用订单')

class report_purchase(http.Controller):
    @http.route(['/report/zc_tr.report_purchase'], type='http', auth='user', multilang=True)
    def report_purchase(self, **data):
        data = simplejson.loads(data['options'])
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook()
            data_sheet = xls_wookbook.add_sheet('data')

            style = xlwt.easyxf(
                'font: height 250;'
                'alignment: vert center, horizontal center;'
                'borders: left thin, right thin, top thin, bottom thin;'
                )

            header_style = xlwt.easyxf(
                'font: height 250, bold True;'
                'borders: left thin, right thin, top thin, bottom thin;'
                'align: vertical center, horizontal center;'
                )

            header_list = [
                u'合同编号', u'供应商', u'签订人', u'合同签订日期', u'材料名称', 
                u'分类', u'材料编码', u'规格描述', u'单价', u'合同数', u'入库数', 
                u'合同金额', u'总合同金额', u'已报销金额', u'已付款金额', u'已入库金额', 
                u'欠款', u'是否执行完毕'
            ]

            [data_sheet.write(0, row, line, style) for row, line in enumerate(header_list)]

            current_row = 1
            for record in data.itervalues():
                vals = record.get('data')

            
                data_sheet.write(current_row, 0, vals.get('name') and vals.get('name') or '', style)
                data_sheet.write(current_row, 1, vals.get('partner') and vals.get('partner') or '', style)
                data_sheet.write(current_row, 2, vals.get('user_name') and vals.get('user_name') or '', style)
                data_sheet.write(current_row, 3, vals.get('date_order') and vals.get('date_order') or '', style)
                data_sheet.write(current_row, 12, vals.get('order_price') and vals.get('order_price') or '', style)
                data_sheet.write(current_row, 13, vals.get('invoice_price') and vals.get('invoice_price') or 0, style)
                data_sheet.write(current_row, 14, vals.get('voucher_price') and vals.get('voucher_price') or 0, style)
                data_sheet.write(current_row, 15, vals.get('delivery_price') and vals.get('delivery_price') or 0, style)
                data_sheet.write(current_row, 16, vals.get('own_price') and vals.get('own_price') or 0, style)
                data_sheet.write(current_row, 17, vals.get('is_done') and vals.get('is_done') or '', style)

                if not record.get('line'):
                    current_row += 1
                    continue

                for line in record.get('line').itervalues():
                    data_sheet.write(current_row, 4, line.get('name') and line.get('name') or '', style)
                    data_sheet.write(current_row, 5, line.get('category') and line.get('category') or '', style)
                    data_sheet.write(current_row, 6, line.get('default_code') and line.get('default_code') or '', style)
                    data_sheet.write(current_row, 7, line.get('desc') and line.get('desc') or '', style)
                    data_sheet.write(current_row, 8, line.get('price_unit') and line.get('price_unit') or 0, style)
                    data_sheet.write(current_row, 9, line.get('quantity') and line.get('quantity') or 0, style)
                    data_sheet.write(current_row, 10, line.get('delivery_qty') and line.get('delivery_qty') or 0, style)
                    data_sheet.write(current_row, 11, line.get('order_price') and line.get('order_price') or 0, style)

                    current_row += 1

            for x, i in enumerate([2, 2, 2, 2, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]):
                data_sheet.col(x).width = 2560 * i

            for x in range(0, row):
                data_sheet.row(x).height_mismatch = 1
                data_sheet.row(x).height = 500

            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=purchase_order_sum.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'该截至日期之前不存在使用订单')

class report_material(http.Controller):
    @http.route(['/report/zc_tr.report_material'], type='http', auth='user', multilang=True)
    def report_material(self, **data):
        data = simplejson.loads(data['options'])
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook()
            data_sheet = xls_wookbook.add_sheet('data')

            style = xlwt.easyxf(
                'font: height 250;'
                'alignment: vert center, horizontal center;'
                'borders: left thin, right thin, top thin, bottom thin;'
                )

            header_style = xlwt.easyxf(
                'font: height 250, bold True;'
                'borders: left thin, right thin, top thin, bottom thin;'
                'align: vertical center, horizontal center;'
                )

            header_list = [u'存货编码', u'名称', u'型号', u'期初存量', 
                           u'入库数量累计', u'出库数量累计', u'结存']

            [data_sheet.write(0, num, line, header_style) for num, line in enumerate(header_list)]

            for num, line in enumerate(data):
                data_sheet.write(num + 1, 0, line.get('default_code'), style)
                data_sheet.write(num + 1, 1, line.get('pc_name'), style)
                data_sheet.write(num + 1, 2, line.get('name'), style)
                data_sheet.write(num + 1, 3, line.get('before_qty'), style)
                data_sheet.write(num + 1, 4, line.get('in_qty'), style)
                data_sheet.write(num + 1, 5, line.get('out_qty'), style)
                data_sheet.write(num + 1, 6, line.get('after_qty'), style)

            for x, i in enumerate([2, 2, 2, 2, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]):
                data_sheet.col(x).width = 2560 * i

            for x in range(0, num + 2):
                data_sheet.row(x).height_mismatch = 1
                data_sheet.row(x).height = 500

            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=stockquntity.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'该截至日期之前不存在使用订单')

class report_financial_purchase(http.Controller):
    @http.route(['/report/zc_tr.report_financial_purchase'], type='http', auth='user', multilang=True)
    def report_financial_purchase(self, **data):
        data = simplejson.loads(data['options'])
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook()
            data_sheet = xls_wookbook.add_sheet('data')

            style = xlwt.easyxf(
                'font: height 250;'
                'alignment: vert center, horizontal center;'
                'borders: left thin, right thin, top thin, bottom thin;'
                )

            header_style = xlwt.easyxf(
                'font: height 250, bold True;'
                'borders: left thin, right thin, top thin, bottom thin;'
                'align: vertical center, horizontal center;'
                )

            header_list = [u'合同号', u'供应商', u'材料编码', u'物料名称', u'规格型号', 
                           u'单位', u'合同数量', u'合同单价', u'总合同金额']

            [data_sheet.write(0, num, line, header_style) for num, line in enumerate(header_list)]

            for num, line in enumerate(data):
                data_sheet.write(num + 1, 0, line.get('order_ref'), style)
                data_sheet.write(num + 1, 1, line.get('partner_id'), style)
                data_sheet.write(num + 1, 2, line.get('default_code'), style)
                data_sheet.write(num + 1, 3, line.get('categ_name'), style)
                data_sheet.write(num + 1, 4, line.get('name'), style)
                data_sheet.write(num + 1, 5, line.get('product_uom'), style)
                data_sheet.write(num + 1, 6, line.get('product_uom_qty'), style)
                data_sheet.write(num + 1, 7, line.get('price_unit'), style)
                data_sheet.write(num + 1, 8, line.get('amount'), style)

            for x, i in enumerate([2, 2, 2, 2, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]):
                data_sheet.col(x).width = 2560 * i

            for x in range(0, num + 2):
                data_sheet.row(x).height_mismatch = 1
                data_sheet.row(x).height = 500

            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=purchasesum3.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'该截至日期之前不存在使用订单')
'''
class report_mrp_bom(http.Controller):
    @http.route(['/report/zc_tr.report_mrp_bom'], type='http', auth='user', multilang=True)
    def report_mrp_bom(self, **data):
        data = simplejson.loads(data['options'])
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook()
            data_sheet = xls_wookbook.add_sheet('data', cell_overwrite_ok = True)

            style = xlwt.easyxf(
                'font: height 250;'
                'alignment: vert center, wrap on;'
                'borders: left thin, right thin, top thin, bottom thin;'
                )

            list_style = xlwt.easyxf(
                'font: height 250;'
                'alignment: vert center, horizontal center;'
                'borders: left thin, right thin, top thin, bottom thin;'
                )

            header_style = xlwt.easyxf(
                'font: height 250, bold True;'
                'borders: left thin, right thin, top thin, bottom thin;'
                'align: vertical center, horizontal center;'
                )

            for row in range(0, 4):
                [data_sheet.write(row, col, '', style) for col in range(1, 11)]

            header_list_left = [u'产品中文名称', u'产品英文名称', u'产品型号', u'产品编号']
            header_list_right = [u'文件名称', u'文件代号', u'文件版本', u'总合同金额']

            for num, header in enumerate(header_list_left):
                data_sheet.write_merge(num, num, 0, 1, header, list_style)

            for num, header in enumerate(header_list_right):
                data_sheet.write_merge(num, num, 7, 8, header, list_style)

            data_sheet.write(2, 2, data['header']['name'], list_style)
            data_sheet.write(3, 2, data['header']['default_code'], list_style)

            header_list = [u'序号', u'腾锐编码', u'类别', u'型号', u'厂商',
                           u'描述', u'封装', u'数量', u'位号', u'备注']

            [data_sheet.write(num + 2, index, val, header_style) for index, val in enumerate(header_list)]

            for line in data['line']:
                data_sheet.write(num + 3, 0, line.get('sequence') or '', style)
                data_sheet.write(num + 3, 1, line.get('default_code') or '', style)
                data_sheet.write(num + 3, 2, line.get('category') or '', style)
                data_sheet.write(num + 3, 3, line.get('name') or '', style)
                data_sheet.write(num + 3, 4, line.get('manufacturer') or '', style)
                data_sheet.write(num + 3, 5, line.get('description') or '', style)
                data_sheet.write(num + 3, 6, line.get('package') or '', style)
                data_sheet.write(num + 3, 7, line.get('product_qty') or 0, style)
                data_sheet.write(num + 3, 8, line.get('item_number') or '', style)
                data_sheet.write(num + 3, 9, line.get('note') or '', style)

                num += 1


            for x, i in enumerate([1, 2, 2, 2, 2, 2, 2, 1, 2, 2]):
                data_sheet.col(x).width = 2560 * i

            for x in range(0, num + 4):
                data_sheet.row(x).height_mismatch = 1
                data_sheet.row(x).height = 450

            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=bomlist.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'没有数据')
class report_out_invoice(http.Controller):
    @http.route(['/report/zc_tr.report_out_invoice'], type='http', auth='user', multilang=True)
    def report_out_invoice(self, **data):
        data = simplejson.loads(data['options'])
        if data:
            xls = StringIO.StringIO()
            xls_wookbook = xlwt.Workbook()
            ds = xls_wookbook.add_sheet('data', cell_overwrite_ok = True)

            style = xlwt.easyxf(
                'font: height 250;'
                'alignment: wrap on;'
                'align: vertical center;'
                'borders: left thin, right thin, top thin, bottom thin;'
                )

            header_style = xlwt.easyxf(
                'font: height 350;'
                'align: vertical center, horizontal center;'
                )

            ds.write_merge(0,0,0,8,u'发票申请表(2013年版)',header_style)
            ds.write_merge(1,1,0,8,datetime.now().strftime('%Y-%m-%d'),header_style)
            
            ds.write_merge(2,2,0,0,u'合同编号',style)
            ds.write_merge(2,2,1,2,data['header']['sale_number'],style)
            ds.write_merge(2,2,3,3,u'合同总额',style)
            ds.write_merge(2,2,4,5,data['header']['sale_total'],style)
            ds.write_merge(2,2,6,7,u'项目号',style)
            ds.write_merge(2,2,8,8,data['header']['project'],style)
            
            ds.write_merge(3,3,0,0,u'发票类别',style)
            ds.write_merge(3,3,1,2,(u'█' if data['header']['category'] == 'c1' else u'□') + u'增值税普票',style)
            ds.write_merge(3,3,3,3,(u'█' if data['header']['category'] == 'c2' else u'□') + u'增值税专票',style)
            ds.write_merge(3,3,4,4,(u'█' if data['header']['category'] == 'c3' else u'□') + u'营改增普票',style)
            ds.write_merge(3,3,5,5,(u'█' if data['header']['category'] == 'c4' else u'□') + u'营改增专票',style)
            ds.write_merge(3,3,6,7,(u'█' if data['header']['category'] == 'c5' else u'□') + u'服务业发票',style)
            ds.write_merge(3,3,8,8,(u'█' if data['header']['category'] == 'c6' else u'□') + u'收据',style)
            
            ds.write_merge(4,4,0,0,u'发票号码',style)
            ds.write_merge(4,4,1,2,u'',style)
            ds.write_merge(4,4,3,3,u'',style)
            ds.write_merge(4,4,4,4,u'',style)
            ds.write_merge(4,4,5,5,u'',style)
            ds.write_merge(4,4,6,7,u'',style)
            ds.write_merge(4,4,8,8,u'',style)
            
            ds.write_merge(5,9,0,0,u'客户信息（如申请开具增值税专用发票此部分信息务必完整、准确）',style)
            
            ds.write_merge(5,5,1,2,u'单位名称',style)
            ds.write_merge(5,5,3,8,data['header']['customer_name'],style)
            
            ds.write_merge(6,6,1,2,u'税务登记号',style)
            ds.write_merge(6,6,3,8,data['header']['customer_vat'],style)
            
            ds.write_merge(7,8,1,2,u'地址、电话',style)
            ds.write_merge(7,8,3,8,data['header']['customer_add'],style)
            
            ds.write_merge(9,9,1,2,u'银行账号',style)
            ds.write_merge(9,9,3,8,data['header']['customer_bank'],style)
            
            ds.write_merge(10,14,0,0,u'开票内容',style)
            ds.write_merge(10,10,1,1,u'类别',style)
            ds.write_merge(10,10,2,4,u'开票名称',style)
            ds.write_merge(10,10,5,5,u'规格型号',style)
            ds.write_merge(10,10,6,6,u'数量',style)
            ds.write_merge(10,10,7,7,u'单价',style)
            ds.write_merge(10,10,8,8,u'金额',style)
            
            i = 1
            for line in data['line']:
                ds.write_merge(10+i,10+i,1,1,u'□软件  □硬件  □服务',style)
                ds.write_merge(10+i,10+i,2,4,line['name'],style)
                ds.write_merge(10+i,10+i,5,5,line['category'],style)
                ds.write_merge(10+i,10+i,6,6,line['quantity'],style)
                ds.write_merge(10+i,10+i,7,7,line['price_unit'],style)
                ds.write_merge(10+i,10+i,8,8,line['price_subtotal'],style)
                i = i + 1
                if i == 5:
                    break
            j = 0
            while j < 5 - i:
                ds.write_merge(10+i+j,10+i+j,1,1,u'□软件  □硬件  □服务',style)
                ds.write_merge(10+i+j,10+i+j,2,4,u'',style)
                ds.write_merge(10+i+j,10+i+j,5,5,u'',style)
                ds.write_merge(10+i+j,10+i+j,6,6,u'',style)
                ds.write_merge(10+i+j,10+i+j,7,7,u'',style)
                ds.write_merge(10+i+j,10+i+j,8,8,u'',style)
                j = j+1              
            
            ds.write_merge(15,16,0,0,u'发票邮寄信息',style)
            ds.write_merge(15,15,1,2,u'收件人',style)
            ds.write_merge(15,15,3,3,data['header']['contact'],style)
            ds.write_merge(15,15,4,4,u'电话',style)
            ds.write_merge(15,15,5,6,data['header']['phone'],style)
            ds.write_merge(15,15,7,7,u'邮编',style)
            ds.write_merge(15,15,8,8,data['header']['post'],style)
            
            ds.write_merge(16,16,1,2,u'收件人地址',style)
            ds.write_merge(16,16,3,8,data['header']['add'],style)
            
            ds.write_merge(17,18,0,0,u'开票原因：',style)
            ds.write_merge(17,17,1,4,u'回款类别：□预付款、□到货款、□初验款、□终验款、□尾款、□全款',style)
            ds.write_merge(18,18,1,4,u'其它需要：（除以上原因外的开票）',style)
            ds.write_merge(17,18,5,6,u'预计回款时间',style)
            ds.write_merge(17,18,7,8,u'',style)
            
            ds.write_merge(19,19,0,0,u'业务员',style)
            ds.write_merge(19,19,1,3,u'',style)
            ds.write_merge(20,20,0,0,u'商务负责人',style)
            ds.write_merge(20,20,1,3,u'',style)
            ds.write_merge(21,21,0,0,u'部门经理',style)
            ds.write_merge(21,21,1,3,u'',style)
            ds.write_merge(19,21,4,8,u'中心领导审批',style)
            ds.write_merge(22,23,0,0,u'财务审批',style)
            ds.write_merge(22,23,1,3,u'',style)
            ds.write_merge(24,24,0,0,u'领票人',style)
            ds.write_merge(24,24,1,3,u'',style)
            ds.write_merge(22,24,4,8,u'备注',style)
            
            ds.write_merge(25,25,0,8,u'注意：所有签名必须本人手签。')
            
            for row, i in enumerate([2, 1, 1, 2, 2, 2, 1, 1, 2]):
                ds.col(row).width = 2400 * i #如B列宽度不对请调整此数字
            for x in [8,11,12,13,14,17,18]:
                ds.row(x).height_mismatch = 1
                ds.row(x).height = 900
            
            xls_wookbook.save(xls)
            xls.seek(0)
            content = xls.read()

            return request.make_response(content, headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=invoice2.xls;')
            ])
        else:
            raise osv.except_osv(u'错误!', u'没有数据')
class report_purchase_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_purchase_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                'rmb_upper': self._rmb_upper,
            })

        self.context = context
    def _rmb_upper(self, value):
        """
        人民币大写
        来自：http://topic.csdn.net/u/20091129/20/b778a93d-9f8f-4829-9297-d05b08a23f80.html
        传入浮点类型的值返回 unicode 字符串
        """
        rmbmap  = [u"零",u"壹",u"贰",u"叁",u"肆",u"伍",u"陆",u"柒",u"捌",u"玖"]
        unit = [u"分",u"角",u"元",u"拾",u"佰",u"仟",u"万",u"拾",u"佰",u"仟",u"亿",
                u"拾",u"佰",u"仟",u"万",u"拾",u"佰",u"仟",u"兆"]

        nums = map(int,list(str('%0.2f'%value).replace('.','')))
        words = []
        zflag = 0   #标记连续0次数，以删除万字，或适时插入零字
        start = len(nums)-3
        for i in range(start, -3, -1):   #使i对应实际位数，负数为角分
            if 0 != nums[start-i] or len(words) == 0:
                if zflag:
                    words.append(rmbmap[0])
                    zflag = 0
                words.append(rmbmap[nums[start-i]])
                words.append(unit[i+2])
            elif 0 == i or (0 == i%4 and zflag < 3): #控制‘万/元’
                words.append(unit[i+2])
                zflag = 0
            else:
                zflag += 1

        if words[-1] != unit[0]:    #结尾非‘分’补整字
            words.append(u"整")
        return ''.join(words)
class report_po_invoice(osv.AbstractModel):
    _name = 'report.zc_tr.report_purchase_invoice'
    _inherit = 'report.abstract_report'
    _template = 'zc_tr.report_purchase_invoice'
    _wrapped_report_class = report_purchase_invoice
    
class report_po_voucher(osv.AbstractModel):
    _name = 'report.zc_tr.report_print_account_voucher'
    _inherit = 'report.abstract_report'
    _template = 'zc_tr.report_print_account_voucher'
    _wrapped_report_class = report_purchase_invoice

'''