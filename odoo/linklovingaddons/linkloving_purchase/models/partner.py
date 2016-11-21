# -*- coding: utf-8 -*-
from openerp import models, fields, _


class Partner(models.Model):
    _inherit = 'res.partner'
    customer_level = fields.Many2one('res.partner.level', string=_('Customer Level'))
    supplier_level = fields.Many2one('res.partner.level', string=_('Supplier Level'))


class Company(models.Model):
    _inherit = 'res.company'
    official_seal = fields.Binary(string=u'公司公章')
