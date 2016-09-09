# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, exceptions, api, _


class StockMoveCheckDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        trans_prod_num = dict()
        pick_prod_num = dict()
        for movelist in self.picking_id.move_lines:
            if movelist.product_id.id in pick_prod_num.keys():
                pick_prod_num[movelist.product_id.id] += movelist.product_uom_qty
            else:
                pick_prod_num[movelist.product_id.id] = movelist.product_uom_qty
            
        for lstits in self.item_ids:
            pid = lstits.product_id.id
            if pid in trans_prod_num.keys():
                trans_prod_num[pid] += lstits.quantity
            else:
                trans_prod_num[pid] = lstits.quantity
                
        for key,value in trans_prod_num.items():
            if (key in pick_prod_num.keys() and value > pick_prod_num[key]) or not pick_prod_num.has_key(key):
                raise exceptions.Warning(
                    _(u'产品"%s"移动的数量不能大于订单产品数量！') %
                    self.item_ids.search([('product_id.id', '=', key)])[0].product_id.name)
        return super(StockMoveCheckDetails, self).do_detailed_transfer()
    
    
                
  
    
    