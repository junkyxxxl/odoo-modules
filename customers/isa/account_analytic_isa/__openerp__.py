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
    'name': 'ISA s.r.l. - Analytic Accounting Module',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """
Installa tutti i moduli ISA sulla contabilità.

       """,
    'author': 'ISA srl',
    'depends': ['sale',
                'project',
                'hr_timesheet_invoice',
                'account_analytic_analysis',
                'account',
                ],
    'data': ['security/ir.model.access.csv',
             'views/account_analytic_account_view.xml',
             'views/account_analytic_areahb_view.xml',
             'views/project_closing_category_view.xml',
             'wizard/hr_timesheet_invoice_create_view.xml',
             'wizard/hr_timesheet_invoice_periodic_view.xml',
             'wizard/hr_timesheet_invoice_create_final_view.xml',
             'menu_item.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
