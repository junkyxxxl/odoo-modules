# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 ISA s.r.l. (<http://www.isa.it>).
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
    'name': 'ISA s.r.l. - Project Module (Internal production)',
    'version': '0.9',
    'category': 'Project Management',
    'author': 'ISA srl',
    'depends': ['web',
                'project',
                'project_issue',
                'account',
                'account_analytic_isa',
                ],
    'data': ['views/project_view.xml',
             'views/project_issue_view.xml',
             'views/project_issue_category_view.xml',
             'views/project_category_view.xml',
             'views/project_task_view.xml',
             'views/project_task_category_view.xml',
             'views/project_task_work_view.xml',
             'views/project_task_work_type_view.xml',
             'views/project_contract_view.xml',
             'views/project_contract_line_view.xml',
             'views/project_task_type_view.xml',
             'views/project_custom_isa.xml',
             'wizard/wizard_select_date_view.xml',
             'wizard/wizard_manage_works_view.xml',
             'wizard/wizard_manage_works_line_view.xml',
             'security/ir.model.access.csv',
             'menu_item.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
