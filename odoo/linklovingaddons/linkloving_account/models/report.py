# -*- coding: utf-8 -*-

from openerp import api, models


class PaymentInvoicePool(models.AbstractModel):
    _name = 'report.linkloving_account.report_payment_invoice'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('linkloving_account.report_payment_invoice')
        partner_id = self.env[report.model].browse(self.id).partner_id.id
        pool_ids = self.env['account.pool'].search([('partner_id', '=', partner_id)])
        in_amount = 0
        out_amount = 0
        for p in pool_ids:
            if p.inv_id:
                in_amount += p.inv_id.amount_total
            else:
                out_amount += p.voucher_id.amount
        balance = in_amount - out_amount
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(self.id),
            'pool_ids': pool_ids,
            'in_amount': in_amount,
            'out_amount': out_amount,
            'balance': balance
        }
        print pool_ids
        print self.env[report.model].browse(self.id)
        print 'dddddddddddd'
        return report_obj.render('linkloving_account.report_payment_invoice', docargs)
