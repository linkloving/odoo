# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class AccountAmountReceived(models.Model):
    """

    """
    _name = 'account.amount.receive'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    name = fields.Char()
    amount = fields.Float(string='金额')
    account = fields.Char(string='账号')
    remark = fields.Text(string='备注')
    customer_id = fields.Many2one('res.partner', string='客户')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('confirm', 'Confirm Account'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], 'State', readonly=True, default='draft')

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("金额必须大于0")

    @api.multi
    def confirm(self):
        self.state = 'posted'

    @api.multi
    def reject(self):
        self.state = 'draft'

    @api.multi
    def unlink(self):
        for budget in self:
            if budget.state not in ('draft'):
                raise osv.except_osv(u'错误!', u'不能删除非草稿状态的！！！')
        return super(AccountAmountReceived, self).unlink()
