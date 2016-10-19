# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv
import datetime


class AccountInvoicePool(models.Model):
    """
    发票池管理
    """
    _name = 'account.invoice.pool'
    _order = 'create_date desc'
    name = fields.Char()
    partner_id = fields.Many2one('res.partner')
    receive_id = fields.Many2one('account.receive')
    inv_id = fields.Many2one('account.invoice')
    payment_amount = fields.Float(related='receive_id.amount')
    inv_amount = fields.Float(related='inv_id.amount_total')
    balance = fields.Float(compute='_get_balance')

    @api.one
    @api.depends('payment_amount', 'inv_id')
    def _get_balance(self):
        self.balance = self.inv_amount - self.payment_amount
