# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class ProductProduct(models.Model):
    """
       添加多级报价
    """
    _inherit = 'product.template'
    price1 = fields.Float(string='1级价')
    price2 = fields.Float(string='2级价')
    price3 = fields.Float(string='3级价')
    price1_tax = fields.Float(string='1级含税价')
    price2_tax = fields.Float(string='2级含税价')
    price3_tax = fields.Float(string='3级含税价')


