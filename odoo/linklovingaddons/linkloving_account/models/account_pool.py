from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv


class AccountPool(models.Model):
    _name = 'account.pool'
    partner_id = fields.Many2one('res.partner')
    inv_id = fields.Many2one('account.invoice')
    payment_id = fields.Many2one('account.receive')
    sub_in = fields.Float(compute='_get_sub_in')
    sub_out = fields.Float(compute='_get_sub_out')

    @api.one
    @api.depends('payment_id')
    def _get_sub_in(self):
        self.sub_in = -self.payment_id.amount

    @api.one
    @api.depends('inv_id')
    def _get_sub_in(self):
        self.sub_out = -self.inv_id.amount_total
