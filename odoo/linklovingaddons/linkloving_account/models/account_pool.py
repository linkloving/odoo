# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class AccountPool(models.Model):
    _name = 'account.pool'
    _inherit = 'mail.thread'
    partner_id = fields.Many2one('res.partner')
    inv_id = fields.Many2one('account.invoice')
    voucher_id = fields.Many2one('account.voucher')
    period_id = fields.Many2one('account.period', 'Period', required=True, compute='get_period_id', store=True)
    sub_in = fields.Float(compute='_get_sub_in')
    sub_out = fields.Float(compute='_get_sub_out')
    remain_amount = fields.Float(compute='_get_remain_amount')
    state = fields.Selection([
        ('draft', '草稿'),
        ('posted', '提交'),
    ], 'State', readonly=True, default='draft')

    @api.one
    @api.depends('inv_id', 'voucher_id')
    def get_period_id(self):
        if self.voucher_id:
            self.period_id = self.voucher_id.period_id
        else:
            self.period_id = self.inv_id.period_id

    @api.one
    @api.depends('inv_id')
    def _get_sub_in(self):
        amount = 0.0
        if self.inv_id.state not in ['draft', 'cancel']:
            amount = self.inv_id.amount_total
        self.sub_in = amount

    @api.one
    @api.depends('voucher_id')
    def _get_sub_out(self):
        self.sub_out = self.voucher_id.amount

    @api.one
    @api.depends('sub_in', 'sub_out')
    def _get_remain_amount(self):
        self.remain_amount = self.sub_out - self.sub_in

    @api.model
    def create(self, vals):
        return super(AccountPool, self).create(vals)
