# -*- coding: utf-8 -*-
{
    'name': "linkloving_sale",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Linklove",
    'website': "http://www.Linkloving.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_stock', 'product', 'linkloving_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'view/sale_view.xml',
        'view/payment_view.xml',
        'sale_increase_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}