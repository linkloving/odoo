# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp.osv import osv, fields
class product_template(osv.Model):
    _inherit = 'product.template'

    _columns = {
        'product_sepcs': fields.char(u'product specifation'),
        }
