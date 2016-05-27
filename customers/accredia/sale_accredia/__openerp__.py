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
    'name': 'Accredia - Sales',
    'version': '0.1',
    'category': '',
    'author': 'ISA srl',
    'depends': ['sale',
                'project_accredia',
                'hr_timesheet_invoice',
                ],
    'data': ['views/sale_view.xml',
             'views/project_task_view.xml',
             ],
    'auto_install': False,
    'demo': [],
    'test': [],
    'installable': True,
    'certificate': '',
}
