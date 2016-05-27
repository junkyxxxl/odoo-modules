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
    'name': 'Accredia - Invoice on Timesheets Module',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'author': 'ISA srl',
    'depends': ['account',
                'hr_timesheet_invoice',
                'hr_timesheet_sheet',
                'project',
                ],
    'data': ['views/account_analytic_timesheet_type_view.xml',
             'views/hr_analytic_timesheet_view.xml',
             'views/hr_timesheet_sheet_view.xml',
             'views/hr_timesheet_invoice_view.xml',
             'wizard/hr_timesheet_invoice_select_view.xml',
             'wizard/hr_timesheet_invoice_create_view.xml',
             'wizard/hr_timesheet_invoice_create_final_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
