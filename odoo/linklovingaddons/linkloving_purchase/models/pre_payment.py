# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class AccountPrePayment(models.Model):
    """
    设置预付款
    """
    _name = 'account.prepayment'
    name = fields.Char()
    po_id = fields.Many2one('purchase.order', string='Purchase Order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel')
    ], default='draft')
    description = fields.Text(string='Description')
    amount = fields.Float(string='Amount')
