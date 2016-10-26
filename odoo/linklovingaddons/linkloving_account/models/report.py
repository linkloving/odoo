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
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(self.id),
            'pool_ids': pool_ids
        }
        print pool_ids
        print self.env[report.model].browse(self.id)
        print 'dddddddddddd'
        return report_obj.render('linkloving_account.report_payment_invoice', docargs)
