# -*- coding: utf-8 -*-
from openerp import models, fields, api,_




class ljwj_abnormal_shortage_reason(models.Model):
    """
    供应商资质等级
    """
    _name = 'res.partner.level'
    name = fields.Char(string=_('Qualification Level'))


