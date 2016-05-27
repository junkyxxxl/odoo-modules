# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-Today OpenERP S.A. (<http://www.openerp.com>).
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
    'name': 'Bec customization',
    'version': '1.0',
    'category': 'Social Network',
    'sequence': 2,
    'summary': 'Adds subject field to compose',
    'description': 'Adds subject field to compose',
    'author': 'CQ',
    'website': 'http://www.creativiquadrati.it',
    'depends': ['base', 'base_setup','mail'],
    'data': ['views/cq_becmsg.xml',
    ],
    'demo': [
    ],
    'installable': True,
    "active": False,
    'js': [
        'static/src/js/becmailsubject.js',
    ],
    'qweb': [
        'static/src/xml/mail.xml',
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
