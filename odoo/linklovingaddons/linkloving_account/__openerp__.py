# -*- coding: utf-8 -*-
{
    'name': "linkloving_account",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'zc_tr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/payment_view.xml',
        'views/account_pool.xml',
        'views/account_invoice.xml',
        'views/account_ir_sequence.xml',
        'views/account_receive.xml',
        'templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
