# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    "name": "ISA s.r.l. - HR Overtime Management",
    "version": "0.1",
    "author": "ISA srl",
    "category": "Generic Modules/Human Resources",
    "website": "www.isa.it",
    'depends': ['hr',
                'resource',
                ],
    'data': ['security/ir.model.access.csv',
             'security/ir_rule.xml',
             'views/hr_overtime_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
