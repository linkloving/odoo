# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class AccountInvoice(models.Model):
    """

    """
    _inherit = 'account.invoice'
    deduct_amount = fields.Float(string='Deduct Amount')
    deduct_reason = fields.Text(string='Deduct Reason')
