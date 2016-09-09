# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    "name": "zc tr",
    "version": "1.0",
    "author": "ydit",
    "category": "zc",
    "description": """
    This module provide : customizing for TERASPEK

    """,
    'website': 'www.chinamaker.net',
    'sequence': 1,
    'depends': [
        'crm',
        'mrp',
        'mail',
        'account_voucher',
        'account_accountant',
        'sale',
        'stock',
        'stock_account',
        'purchase',
        'account',
        'analytic',
        'base',
        'base_action_rule',
        'base_import',
        'base_setup',
        'decimal_precision',
        'email_template',
        'fetchmail',
        'l10n_cn',
        'product',
        'resource',
        'sale_stock',
        'document',
    ],

    "data": [

       
        'wizard/zc_tr_report_view.xml',
        'zc_tr_report.xml',
        'zc_tr_view.xml',
        'tr_workflow.xml',
    ],
    'installable': True,
    'active': False,
}
