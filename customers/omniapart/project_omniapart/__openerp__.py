# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Omniapart - Project',
    'version': '0.1',
    'category': '',
    'description': """
Project per Omniapart
=====================


       """,
    'author': 'ISA srl',
    'depends': ['account',
                'project',
                'web_kanban',
                'base',
                'calendar',
                'mail',
                'hr',
                'hr_timesheet_invoice',
                'l10n_it_base',
                'l10n_it_ea_sector',
                'res_partner_omniapart',
                'account_analytic_analysis',
                'analytic_user_function',
                'sale',
                'portal_project',
                'project_timesheet',
                ],
    'data': ['security/ir.model.access.csv',
             'security/partner_security.xml',
             'data/accreditation.schema.csv',
             'data/accreditation.standard.csv',
             'norme_schemi/accreditation_standard_view.xml',
             'norme_schemi/accreditation_schema_view.xml',
             'project/project_view.xml',
             'task/project_task_view.xml',
             'menu_items.xml',
             'views/project.xml',
             'analytic/analytic_view.xml',
             'analytic/analytic_line_view.xml',
             'hr_timesheet_invoice/hr_timesheet_invoice_create_view.xml',
             'hr_timesheet_invoice/hr_timesheet_invoice_create_final_view.xml',
             'meeting/calendar_event_view.xml',
             'hr/hr_view.xml',
             'res/res_partner_view.xml',
             'sale/sale_view.xml',
             'wizard/wizard_search_invoice.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
