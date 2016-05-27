# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
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
    "name": "ISA s.r.l. - Report employee",
    "version": "0.1",
    "description": "report employee",
    "author": "ISA srl",
    'website': '',
    "depends": ['base',
                'report_webkit',
                'hr',
                'hr_overtime',
                'hr_attendance_isa',
                'hr_holidays_isa',
                'base_res_company_isa',
                'account_financial_report_webkit',
                ],
    "category": "Generic Modules/Webkit Reporting",
    "demo": [],
    "data": ['report/report.xml',
             'wizard/hr_summary_bymonth_view.xml',
             'security/ir.model.access.csv'
             ],
    "installable": True,
    'active': True,
    'certificate': '',
}
