# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class ProductProduct(models.Model):
    """
       添加多级报价
    """
    _inherit = 'product.template'
    price1 = fields.Float(string=u'1级价')
    price2 = fields.Float(string=u'2级价')
    price3 = fields.Float(string=u'3级价')
    price1_tax = fields.Float(string=u'1级含税价')
    price2_tax = fields.Float(string=u'2级含税价')
    price3_tax = fields.Float(string=u'3级含税价')

class ProductPriceDiscount(models.Model):
    """
       添加多级报价
    """
    _name = 'product.price.discount'
    partner_id=fields.Many2one('res.partner')
    product_id=fields.Many2one('product.product')
    price=fields.Float(default=1.00)
    price_tax=fields.Float(default=1.00)

