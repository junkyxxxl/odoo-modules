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
    'name': 'Accredia - HR module',
    'version': '0.2',
    'category': '',
    'author': 'ISA srl',
    'depends': ['mail',
                'email_template',
                'hr',
                'account',
                'account_makeover',
                'base',
                'base_vat',
                'base_isa',
                'web',
                'base_fiscalcode',
                'l10n_it_base',
                'doclite',
                'l10n_it_pec',
                ],
    'data': ['security/entity_changes_group.xml',
             'security/ir.model.access.csv',
             'views/accreditation_locations_view.xml',
             'views/accreditation_institution_members_view.xml',
             'views/accreditation_units_categories_view.xml',
             'views/accreditation_units_view.xml',
             'views/res_partner_view.xml',
             'views/accreditation_entity_categories_view.xml',
             'views/accreditation_persons_units_views.xml',
             'views/accreditation_roles_view.xml',
             'views/accreditation_person_roles_view.xml',
             'views/res_users_view.xml',
             'views/hr_employee_view.xml',
             'views/accreditation_changelog_view.xml',
             'views/accreditation_unit_changelog_view.xml',
             'views/accreditation_jobs_views.xml',
             'views/accreditation_persons_units_type_views.xml',
             'views/hr_department_view.xml',
             'views/accreditation_qualifications_view.xml',
             'wizard/hr_accredia_changes_entity_view.xml',
             'wizard/hr_accredia_changes_unit_view.xml',
             'menu_items.xml',
             ],
    'demo': [],
    'qweb': ["static/src/xml/base.xml",
             ],
    'test': [],
    'sequence': 250,
    'installable': True,
    'active': False,
    'certificate': '',
}
