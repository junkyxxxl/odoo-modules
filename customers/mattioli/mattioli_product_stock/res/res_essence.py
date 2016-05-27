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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class essence(osv.osv):
    _name = "res.essence"
    _description = "Essences"

    def _check_code(self, cr, uid, ids, context=None):
        for essence in self.browse(cr, uid, ids, context=context):
            if len(essence.code) == 3:
                for letter in essence.code:
                    if not ('A' <= letter <= 'Z') and not ('0' <= letter <= '9'):
                        return False
            else:
                return False
        return True

    _columns = {'name': fields.char('Name', required=True),
                'code': fields.char('Local Code', size=3, required=True, help='This field is used to set/get locales for user'),
                }

    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of the essence must be unique !'),
                        ('code_uniq', 'unique (code)', 'The code of the essence must be unique !'),
                        ]

    _constraints = [(_check_code, 'Invalid code format specified. Please type a 3-letters uppercase code without special symbols.', ['code'])
                    ]
