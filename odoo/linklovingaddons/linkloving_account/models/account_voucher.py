# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

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
