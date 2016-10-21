# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def button_proforma_voucher(self):
        context = self._context
        account_receive_id = context.get('account_receive_id')
        account_payment_id = context.get('account_payment_id')
        if account_payment_id:
            account_payment = self.env['account.payment'].browse(account_payment_id)
            account_payment.state = 'done'
        if account_receive_id:
            account_receive = self.env['account.receive'].browse(account_receive_id)
            account_receive.state = 'done'
        self.signal_workflow('proforma_voucher')
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def create(self, vals):
        voucher = super(AccountVoucher, self).create(vals)
        data = {
            'partner_id': vals.get('partner_id'),
            'voucher_id': voucher.id
        }
        # 资金池
        self.env['account.pool'].create(data)

        return voucher
