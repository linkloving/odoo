# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def button_proforma_voucher(self):
        account_receive_id = self._context.get('account_receive_id')
        if account_receive_id:
            account_receive = self.env['account.receive'].browse(account_receive_id)
            if account_receive.receive_type == 'pre':
                account_receive.state = 'deduct'
            else:
                account_receive.state = 'done'
        self.signal_workflow('proforma_voucher')
        return {'type': 'ir.actions.act_window_close'}
