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
    _inherit = 'mail.thread'
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
        ('draft', 'Draft'),
        ('unpaid', 'Unpaid'),
        ('paid', '确认'),
        ('done', '预付申请'),
        ('cancel', 'Cancel')
    ], default='unpaid')
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
    def post(self):
        self.state = 'unpaid'

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
        return super(AccountPayment, self).unlink()

    @api.multi
    def create_voucher(self):
        # todo: 上月预算到当月5号之后作废，不能生成付款
        DATE_FORMAT = "%Y-%m-%d"
        start_date_obj = (datetime.datetime.today().replace(day=1) - datetime.timedelta(1)).replace(day=1)
        start_date = datetime.datetime.strftime(start_date_obj, DATE_FORMAT)
        print start_date

        now_date = datetime.datetime.strftime(datetime.date.today(), DATE_FORMAT)
        print now_date

        day5_obj = (datetime.datetime.today().replace(day=25) - datetime.timedelta(1)).replace(day=25)
        day5 = datetime.datetime.strftime(day5_obj, DATE_FORMAT)
        print day5
        voucher_pool = self.env['account.voucher']

        voucher_ids = []

        for line in self:
            # if line.create_date<start_date or now_date> day5:
            #    raise osv.except_osv(u'错误!',u'预算已经过期(上月预算次月25号后不能再生成付款)')
            voucher_id = voucher_pool.create({'partner_id': line.partner_id.id,
                                              'po': line.po_id.id,
                                              'amount': line.amount,
                                              'account_id': line.partner_id.property_account_payable.id,
                                              'type': 'payment'
                                              }, context=self._context)
            voucher_ids.append(voucher_id.id)

            self.write({'state': 'done'}, context=self._context)
        return {
            'name': '供应商付款',
            'domain': [('id', 'in', voucher_ids)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'context': self._context,
        }
