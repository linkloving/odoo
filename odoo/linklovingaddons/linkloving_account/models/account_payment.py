# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv
import datetime


class AccountPayment(models.Model):
    """
    设置预付款
    """
    _name = 'account.payment'
    _order = 'create_date desc'
    _rec_name = 'amount'
    pay_type = fields.Selection([
        ('1', '预付款'),
        ('2', '正常款'),
    ], default='1')
    name = fields.Char()
    is_deduct = fields.Boolean()
    po_id = fields.Many2one('purchase.order', string='Purchase Order')
    so_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one(related='po_id.partner_id')
    state = fields.Selection([
        ('draft', u'草稿'),
        ('apply', u'付款申请'),
        ('done', u'完成'),
        ('cancel', u'取消')
    ], default='draft')
    description = fields.Text(string='备注')
    amount = fields.Float(string='Amount')

    _sql_constraints = {
        ('name_uniq', 'unique(name)',
         'Name mast be unique!')
    }

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("预付款金额必须大于0")
            if record.amount > record.po_id.amount_total:
                raise ValidationError("预付款总额大于PO金额")
            if record.po_id.pre_payment_ids:
                pre_payment_total = 0
                for p in record.po_id.pre_payment_ids:
                    pre_payment_total += p.amount
                if record.po_id.amount_total < pre_payment_total:
                    raise ValidationError("预付款总额大于PO金额")

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.env[
                               'ir.sequence'].get('account.payment') or '/'
        return super(AccountPayment, self).create(vals)

    @api.multi
    def confirm_prepayment(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def apply(self):
        self.state = 'apply'

    @api.multi
    def set_to_apply(self):
        self.state = 'apply'

    @api.multi
    def cancel(self):
        self.state = 'cancel'

    @api.multi
    def unlink(self):
        for payment in self:
            if payment.state not in ('draft'):
                raise osv.except_osv(u'错误!', u'不能删除非草稿状态的！！！')
        return super(AccountPayment, self).unlink()

    @api.multi
    def invoice_pay_supplier(self):
        return {
            'name': '供应商付款',
            'view_mode': 'form',
            'view_id': self.env.ref('account_voucher.view_vendor_receipt_dialog_form').id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                # 'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.partner_id.id,
                'default_amount': self.amount,
                # 'default_reference': inv.name,
                'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                'default_type': 'payment',
                'type': 'payment',
                'account_payment_id': self.id,
            }
        }
