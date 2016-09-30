# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class AccountPrePayment(models.Model):
    """
    设置预付款
    """
    _name = 'account.prepayment'
    _order = 'create_date desc'
    name = fields.Char()
    po_id = fields.Many2one('purchase.order', string='Purchase Order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel')
    ], default='unpaid')
    description = fields.Text(string='Description')
    amount = fields.Float(string='Amount')
    deduct_amount = fields.Float(string='Pre Payment Deduction')
    check_total = fields.Float(string='Total Pre Payment')

    @api.multi
    def confirm_prepayment(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def pay(self):
        self.state = 'paid'

    @api.multi
    def cancel(self):
        self.state = 'cancel'
