# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class Partner(models.Model):
    """
       添加多级报价
    """
    _inherit = 'res.partner'

    level = fields.Selection([
        (1, '1级'),
        (2, '2级'),
        (3, '3级')
    ],string='客户等级')

