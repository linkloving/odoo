# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class AccountPrePayment(models.Model):
    """
    设置预付款
    """
    _name = 'account.prepayment'
    _inherit = 'mail.thread'
    _order = 'create_date desc'
    name = fields.Char()
    po_id = fields.Many2one('purchase.order', string='Purchase Order')
    so_id = fields.Many2one('sale.order', string='Sale Order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel')
    ], default='unpaid')
    description = fields.Text(string='Description')
    amount = fields.Float(string='Amount')

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




    @api.multi
    def confirm_prepayment(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def pay(self):
        self.state = 'paid'

    @api.multi
    def cancel(self):
        self.state = 'cancel'

    @api.multi
    def unlink(self):
        for payment in self:
            if payment.state not in ('draft'):
                raise osv.except_osv(u'错误!', u'不能删除非草稿状态的！！！')
        return super(AccountPrePayment, self).unlink()
