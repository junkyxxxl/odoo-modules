# -*- coding: utf-8 -*-
{
    "name" : "BEC s.r.l. - Partner Dealers",
    "version" : "1.0",
    "author" : "BeC",
    "category": 'BeC Plugins',
    #'complexity': "easy",
    "description": """
BeC - Partner Dealers
====================================
Create a relationship between the companies through parent_id, type of manufacturer / distributor
    """,
    'website': 'http://www.bec.it',
    "depends" : [
    	"base", 
        "l10n_it_base",
	],
    'data': [
        'view/res_partner_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'application': False,
    'installable': True,
    'css': [
    ],
}
