# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class AccountAmountReceived(models.Model):
    """

    """
    _name = 'account.receive'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    name = fields.Char()
    amount = fields.Float(string='金额')
    deduct_amount = fields.Float(string='被抵扣')
    account = fields.Char(string='账号')
    receive_date = fields.Date(string='收款日期', default=fields.date.today())
    remark = fields.Text(string='备注')
    customer_id = fields.Many2one('res.partner', string='客户')
    receive_id = fields.Many2one('res.users')
    journal_id = fields.Many2one('account.journal', 'Salary Journal')

    receive_type = fields.Selection([
        ('pre', '预收款'),
        ('normal', '正常')
    ], default='normal', string='收款类型')
    state = fields.Selection([
        ('draft', '草稿'),
        ('posted', '提交'),
        ('confirm', '销售确认'),
        ('deduct', '预付款抵扣'),
        ('done', '完成'),
        ('cancel', '取消')
    ], 'State', readonly=True, default='draft')

    _sql_constraints = {
        ('name_uniq', 'unique(name)',
         'Name mast be unique!')
    }

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("金额必须大于0")

    @api.multi
    def post(self):
        self.state = 'posted'

    @api.multi
    def confirm(self):
        self.env['account.pool'].create({
            'partner_id': self.customer_id.id,
            'payment_id': self.id
        })
        self.state = 'confirm'

    @api.multi
    def reject(self):
        self.state = 'draft'

    @api.multi
    def unlink(self):
        for budget in self:
            if budget.state not in ('draft'):
                raise osv.except_osv(u'错误!', u'不能删除非草稿状态的！！！')
        return super(AccountAmountReceived, self).unlink()

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.env[
                               'ir.sequence'].get('account.receive') or '/'
        return super(AccountAmountReceived, self).create(vals)

    @api.multi
    def invoice_pay_customer(self):
        return {
            'name': _("登记收款"),
            'view_mode': 'form',
            'view_id': self.env.ref('account_voucher.view_vendor_receipt_dialog_form').id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_partner_id': self.customer_id.id,
                'default_amount': self.amount,
                'default_reference': self.customer_id.name,
                'close_after_process': True,
                'default_type': 'receipt',
                'type': 'receipt',
                'account_receive_id': self.id
            }
        }
