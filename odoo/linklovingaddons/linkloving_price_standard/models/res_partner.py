# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class Partner(models.Model):
    """
       添加多级报价
    """
    _inherit = 'res.partner'

    level = fields.Selection([
        (1, u'1级'),
        (2, u'2级'),
        (3, u'3级')
    ],string=u'客户等级')

