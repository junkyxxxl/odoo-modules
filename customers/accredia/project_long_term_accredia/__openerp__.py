# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Accredia - Long Term Projects',
    'version': '1.1',
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'category': 'Project Management',
    'images': ['images/project_phase_form.jpeg',
               'images/project_phases.jpeg',
               'images/resources_allocation.jpeg'],
    'depends': ['project',
                'product',
                ],
    'demo': [],
    'test': [],
    'data': ['security/ir.model.access.csv',
             'views/project_user_allocation_view.xml',
             'views/project_task_view.xml',
             'views/project_phase_view.xml',
             'views/project_project_view.xml',
             'views/account_analytic_account_view.xml',
             'views/project_long_term_workflow.xml',
             'menu_item.xml',
             ],
    'installable': True,
    'auto_install': False,
}
