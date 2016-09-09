# -*- encoding: utf-8 -*-
##############################################################################
#
#    DMEMS Base Module
#    Copyright (C) 2014 DMEMS (<http://www.dmems.com>).
#
##############################################################################
{
    'name': 'YDIT Base',
    'version': '1.0',
    'category': 'Customization',
    'sequence': 1000,
    'summary': 'ydit Base',
    'description': """
DM Base
==================================
1.Remove “Your OpenERP is not supported” on screen top
2.add the common option list feature
------------------------------------------------------
    """,
    'author': 'YDIT',
    'website': 'http://www.chinamaker.net',
    'images': [],
    'depends': ['base'],
    'data': [
        'workflow_view.xml',
        'ir_translation_view.xml',
        ],
    'demo': [],
    'test': [],
    #web
    'css' : ['static/src/css/dm.css',],    
    'installable': True,
    'auto_install': False,
    'application': True,
}
