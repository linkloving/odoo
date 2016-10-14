# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class AccountPool(models.Model):
    _name = 'account.pool'
    _inherit = 'mail.thread'
    partner_id = fields.Many2one('res.partner')
    inv_id = fields.Many2one('account.invoice')
    payment_id = fields.Many2one('account.receive')
    # period_id= fields.Many2one('account.period', 'Period', required=True, readonly=True)
    sub_in = fields.Float(compute='_get_sub_in')
    # sub_out = fields.Float(compute='_get_sub_out')
    state = fields.Selection([
        ('draft', '草稿'),
        ('posted', '提交'),
    ], 'State', readonly=True, default='draft')

    @api.one
    @api.depends('payment_id')
    def _get_sub_in(self):
        amount = 0
        if self.payment_id:
            amount = --self.payment_id.amount
        self.sub_in = amount

        # @api.one
        # @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
        # def _compute_amount(self):
        #     self.amount_total_in = sum(line.price_subtotal for line in self.invoice_line)
        #     self.amount_total_out = sum(line.amount for line in self.tax_line)
        #     self.amount_total = self.amount_total_in + self.amount_total_out
        #
        # @api.one
        # @api.depends('inv_id')
        # def _get_sub_in(self):
        #     self.sub_out = -self.inv_id.amount_total
