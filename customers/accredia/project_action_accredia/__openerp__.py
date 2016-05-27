# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Accredia - Project Action',
    'version': '0.1',
    'category': '',
    'author': 'ISA srl',
    'depends': ['doclite',
                'doclite_accredia',
                'account_accredia',
                'accredia_purchase',
                'hr_accredia',
                'project_accredia',
                'sale_accredia',
                ],
    'data': ['security/ir.model.access.csv',
             'views/project_task_work_view.xml',
             'views/accreditation_task_work_log_view.xml',
             'views/accreditation_task_work_type_view.xml',
             'assets.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
