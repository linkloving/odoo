# -*- coding: utf-8 -*-

from openerp import api, models


class PaymentInvoicePool(models.AbstractModel):
    _name = 'report.linkloving_account.q'

    @api.multi
    def render_html(self, data=None):
        print '333333333333333333333333333333333333'
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('linkloving_account.report_payment_invoice')
        partner_id = report.partner_id.id
        pool_ids = self.env['account.pool'].search([('partner_id', '=', partner_id)])
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'pool_ids': '11'
        }
        return report_obj.render('linkloving_account.report_payment_invoice', docargs)
