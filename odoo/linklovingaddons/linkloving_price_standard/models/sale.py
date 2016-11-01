# -*- coding: utf-8 -*-
from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import except_orm
import openerp.addons.decimal_precision as dp
import time
from openerp.osv import osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
                          flag=False, context=None, price_unit=False):
        context = context or {}
        tax_id = context.get('default_tax_id')
        print tax_id

        a, b, tax_id = tax_id[0]
        if len(tax_id) > 1:
            raise osv.except_orm(_('只能定义一种税金!'),
                                 _('请先定义税金.'))

        if not tax_id:
            raise osv.except_orm(_('没有定于税金!'),
                                 _('请先定义税金.'))

        lang = lang or context.get('lang', False)
        if not partner_id:
            raise osv.except_osv(_('No Customer Defined!'),
                                 _('Before choosing a product,\n select a customer in the sales form.'))
        warning = False

        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        tax_obj = self.pool.get('account.tax')
        price_discount_obj = self.pool.get('product.price.discount')
        product_obj = self.pool.get('product.product')
        tax_id = tax_obj.browse(cr, uid, tax_id[0])
        partner = partner_obj.browse(cr, uid, partner_id)
        lang = partner.lang
        context_partner = context.copy()
        context_partner.update({'lang': lang, 'partner_id': partner_id})

        if not product:
            return {'value': {'th_weight': 0,
                              'product_uos_qty': qty}, 'domain': {'product_uom': [],
                                                                  'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False

        fpos = False
        if not fiscal_position:
            fpos = partner.property_account_position or False
        else:
            fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)

        if uid == SUPERUSER_ID and context.get('company_id'):
            taxes = product_obj.taxes_id.filtered(lambda r: r.company_id.id == context['company_id'])
        else:
            taxes = product_obj.taxes_id
        # result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes, context=context)

        if not flag:
            result['name'] = \
                self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n' + product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                          [('category_id', '=', product_obj.uom_id.category_id.id)],
                      'product_uos':
                          [('category_id', '=', uos_category_id)]}
        elif uos and not uom:  # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom:  # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight  # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price


        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                         'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg + "\n\n"
        else:
            ctx = dict(
                context,
                uom=uom or result.get('product_uom'),
                date=date_order,
            )
            # allen modify

            discount_id = price_discount_obj.search(cr, uid, [('partner_id', '=', partner_id),('product_id', '=', product_obj.id)])
            if not discount_id:
                discount_id = price_discount_obj.create(cr, uid, {
                    'partner_id': partner_id,
                    'product_id':product_obj.id
                })
            price = 0.0
            discount = price_discount_obj.browse(cr, uid, discount_id).price
            discount_tax = price_discount_obj.browse(cr, uid, discount_id).price_tax
            if partner.level == 1:
                if not tax_id.amount:
                    price = product_obj.price1 * discount
                else:
                    price = product_obj.price1_tax * discount_tax
            elif partner.level == 2:
                if not tax_id.amount:
                    price = product_obj.price2 * discount
                else:
                    price = product_obj.price2_tax * discount_tax
            elif partner.level == 3:
                if not tax_id.amount:
                    price = product_obj.price3 * discount
                else:
                    price = product_obj.price3_tax * discount_tax
            else:
                pass
            # price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
            #                                                      product, qty or 1.0, partner_id, ctx)[pricelist]
            if price is False:
                price = 0.00
                # warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                #              "You have to change either the product, the quantity or the pricelist.")
                #
                # warning_msgs += _("No valid pricelist line found ! :") + warn_msg + "\n\n"

            else:
                # price = self.pool['account.tax']._fix_tax_included_price(cr, uid, price, taxes,
                #
                #                                                     context['default_tax_id'])


                if not result.get('price_unit'):
                    result.update({'price_unit': price})
                if context.get('uom_qty_change', False):
                    values = {'price_unit': price}
                    if result.get('product_uos_qty'):
                        values['product_uos_qty'] = result['product_uos_qty']
                    print values
                    return {'value': values, 'domain': {}, 'warning': False}
        if warning_msgs:
            warning = {
                'title': _('Configuration Error!'),
                'message': warning_msgs
            }
        return {'value': result, 'domain': domain, 'warning': warning}

    @api.multi
    def write(self, vals):

        for line in self:
            price_unit = vals.get('price_unit')
            price=0.0

            if price_unit:
                product_id = vals.get('product_id') or line.product_id.id
                partner_id = line.order_id.partner_id
                discount_obj = line.env['product.price.discount'].search(
                    [('partner_id', '=', partner_id.id), ('product_id', '=', product_id)])
                if partner_id.level == 1:
                    if not line.tax_id.amount:
                        price = line.product_id.price1
                    else:
                        price = line.product_id.price1_tax
                elif partner_id.level == 2:
                    if not line.tax_id.amount:
                        price = line.product_id.price2
                    else:
                        price = line.product_id.price2_tax
                elif partner_id.level == 3:
                    if not line.tax_id.amount:
                        price = line.product_id.price3
                    else:
                        price = line.product_id.price3_tax
                if price and not line.tax_id.amount and price_unit <> price:
                    discount = price_unit / price
                    discount_obj.price = discount
                elif price and line.tax_id.amount and price_unit <> price:
                    discount_tax = price_unit / price
                    discount_obj.price_tax = discount_tax

        return super(SaleOrderLine, self).write(vals)

    @api.model
    def create(self, vals):
        order_id = self.env['sale.order'].browse(vals.get('order_id'))
        print vals
        _, _, tax_id = vals.get('tax_id')[0]
        tax_id = self.env['account.tax'].browse(tax_id[0])

        price_unit = vals.get('price_unit')
        product_id = self.env['product.product'].browse(vals.get('product_id'))
        price = 0.0
        if price_unit:
            partner_id = order_id.partner_id
            discount_obj = self.env['product.price.discount'].search([('partner_id', '=', partner_id.id), ('product_id', '=', product_id.id)])
            if not discount_obj:
                discount_obj=self.env['product.price.discount'].create({
                    'partner_id':partner_id.id,
                    'product_id':product_id.id
                })

            if partner_id.level == 1:
                if not tax_id.amount:
                    price = product_id.price1
                else:
                    price = product_id.price1_tax
            elif partner_id.level == 2:
                if not tax_id.amount:
                    price = product_id.price2
                else:
                    price = product_id.price2_tax
            elif partner_id.level == 3:
                if not tax_id.amount:
                    price = product_id.price3
                else:
                    price = product_id.price3_tax
            if price and not tax_id.amount and price_unit <> price:
                discount = price_unit / price
                discount_obj.price = discount
            elif price and tax_id.amount and price_unit <> price:
                discount_tax = price_unit / price
                discount_obj.price_tax = discount_tax

        return super(SaleOrderLine, self).create(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'



    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        discount=discount_tax=1.0
        if self.order_line:

            for line in self.order_line:
                discount_id = self.env['product.price.discount'].search(
                    [('partner_id', '=', self.partner_id.id), ('product_id', '=', line.product_id.id)], limit=1)
                if discount_id:
                    discount = discount_id.price
                    discount_tax = discount_id.price_tax
                if self.partner_id.level == 1:
                    if self.tax_id.amount:
                        line.price_unit = line.product_id.price1_tax * discount_tax
                    else:
                        line.price_unit = line.product_id.price1 * discount
                elif self.partner_id.level == 2:
                    if self.tax_id.amount:
                        line.price_unit = line.product_id.price2_tax * discount_tax
                    else:
                        line.price_unit = line.product_id.price2 * discount
                elif self.partner_id.level == 3:
                    if self.tax_id.amount:
                        line.price_unit = line.product_id.price2_tax * discount_tax
                    else:
                        line.price_unit = line.product_id.price2 * discount
