# -*- coding: utf-8 -*-
##############################################################################
#
#    Sales and Invoice Discount Management
#    Copyright (C) 2015 BrowseInfo(<http://www.browseinfo.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    @api.depends('order_line.price_total','discount_amt')
    def _amount_all(self):
        order_discount = 0.0
        for order in self:
            amount_untaxed = amount_tax = 0.0
            order_discount = order.discount_amt
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax - order_discount,
            }) 
            
    @api.depends('discount_amount')
    def _calculate_discount(self):
        res = {}
        discount = 0.0
        for self_obj in self:
            if self_obj.discount_method == 'fix':
                discount = self_obj.discount_amount
                res = discount
                
                self_obj.update({
                    'discount_amt' : res})
                    
            elif self_obj.discount_method == 'per':
                discount = self_obj.amount_untaxed * ((self_obj.discount_amount or 0.0) / 100.0)
                res = discount
                self_obj.update({
                    'discount_amt' : res})
            else:
                res = discount
                self_obj.update({
                    'discount_amt' : res})
            for line_obj in self_obj.order_line:
                if line_obj.discount_method == 'fix':
                    discount += line_obj.discount
                    res = discount
                    self_obj.update({
                    'discount_amt' : res})
                elif line_obj.discount_method == 'per':
                    discount += line_obj.price_unit * ((line_obj.discount or 0.0) / 100.0)
                    res = discount
                    self_obj.update({
                    'discount_amt' : res})
                else:
                    discount += 0.0
                    res = discount
                    self_obj.update({
                    'discount_amt' : res})
        return res
        
    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]

        #override the context to get rid of the default filtering
        result['context'] = {'type': 'in_invoice', 'default_purchase_id': self.id,'default_discount_amt' : self.discount_amt,'default_discount_method' : self.discount_method , 'default_discount_amount' : self.discount_amount , 'default_amount_untaxed' : self.amount_untaxed}
        result['domain'] = "[('purchase_id', '=', %s)]" % self.id
        invoice_ids = sum([order.invoice_ids.ids for order in self], [])
        #choose the view_mode accordingly
        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, invoice_ids)) + "])]"
        elif len(invoice_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = invoice_ids and invoice_ids[0] or False
        return result
        
    discount_method = fields.Selection(
            [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Monetary(compute='_calculate_discount',store=True,string='- Discount',digits_compute=dp.get_precision('Account'),readonly=True)
        
    amount_untaxed = fields.Monetary(string='Untaxed Amount',store=True ,readonly=True,compute='_amount_all',track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', readonly=True, store=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total',readonly=True,store=True,compute='_amount_all',track_visibility='always')
    
    
class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    discount_method = fields.Selection(
            [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
            
    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
