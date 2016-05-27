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
    'name': 'Accredia - Project',
    'version': '0.1',
    'category': 'Project Management',
    'author': 'ISA srl',
    'depends': ['mail',
                'project',
                'project_long_term_accredia',
                'project_work_daily',
                'hr_accredia',
                'product',
                'event',
                'calendar',
                'web_calendar',
                'hr_timesheet_invoice',
                ],
    'data': ['security/template_changes_group.xml',
             'security/ir.model.access.csv',
             'views/accreditation_request_view.xml',
             'views/accreditation_request_schema_view.xml',
             'views/accreditation_request_lines_view.xml',
             'views/accreditation_standard_view.xml',
             'views/accreditation_test_view.xml',
             'views/accreditation_test_list_view.xml',
             'views/accreditation_test_temp_view.xml',
             'views/accreditation_test_list_temp_view.xml',
             'views/accreditation_test_list_category_view.xml',
             'views/accreditation_test_change_type_view.xml',
             'views/accreditation_sector_view.xml',
             'views/account_analytic_account_view.xml',
             'views/project_view.xml',
             'views/accreditation_project_type_view.xml',
             'views/accreditation_task_plan_view.xml',
             'views/project_task_view.xml',
             'views/project_task_type_view.xml',
             'views/project_task_category_view.xml',
             'views/accreditation_task_work_type_view.xml',
             'views/project_task_work_view.xml',
             'views/accreditation_persons_auth_view.xml',
             'views/accreditation_skills_view.xml',
             'views/accreditation_person_events_view.xml',
             'views/accreditation_person_events_temp_view.xml',
             'views/project_config_view.xml',
             'views/res_partner_view.xml',
             'views/project_phase_view.xml',
             'views/project_user_allocation_view.xml',
             'views/calendar_event_view.xml',
             'views/accreditation_roles_view.xml',
             'views/res_users_view.xml',
             'project_custom_accredia.xml',
             'wizard/wizard_final_test_view.xml',
             'wizard/wizard_update_state_view.xml',
             'wizard/wizard_project_create_extension_view.xml',
             'wizard/wizard_task_create_child_view.xml',
             'wizard/wizard_task_create_parent_view.xml',
             'wizard/wizard_manage_works_line_view.xml',
             'wizard/wizard_manage_works_view.xml',
             'wizard/wizard_set_date_view.xml',
             'menu_item.xml',
             'data/accreditation_request_data.xml',
             'data/accreditation_test_list_category_data.xml',
             'data/accreditation_test_change_type_data.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
