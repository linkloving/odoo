# -*- coding: utf-8 -*-
from openerp import models, fields,_


class Partner(models.Model):
    _inherit = 'res.partner'
    customer_level = fields.Many2one('res.partner.level', string=_('Customer Level'))
    supplier_level = fields.Many2one('res.partner.level', string=_('Supplier Level'))
