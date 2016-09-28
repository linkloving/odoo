# -*- coding: utf-8 -*-

from openerp import models, fields, api, _



class linkloving_hr_expense_expense(models.Model):

    _inherit = 'hr.expense.expense'

    po_id = fields.Many2one('purchase.order', ondelete="restrict", string=_("Purchase Order"))
    project_id=fields.Many2one('project.project',ondelete="restrict", string=_("Project"))