# -*- coding: utf-8 -*-
{
    "name" : "BEC s.r.l. - Confronti",
    "version" : "1.0",
    "author" : "BeC",
    "category": 'BeC Plugins',
    #'complexity': "easy",
    "description": """
BeC - Comparisons
====================================
Managing comparisons sent and received by companies
""",
    'website': 'http://www.bec.it',
    "depends" : [
    	"base",
	],
    'data': [
        'view/res_compare_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'application': False,
    'installable': True,
    'css': [
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
