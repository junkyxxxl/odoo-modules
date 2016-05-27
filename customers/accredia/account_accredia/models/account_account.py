# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import orm


class AccountAccount(orm.Model):
    _inherit = 'account.account'

    def get_max_code(self, cr, uid, ids, parent_id):
        reads = self.read(cr, uid, parent_id, ['code'])
        max_code = None
        if reads['code']:
            base_code = reads['code'][:4]
            cr.execute("SELECT MAX(code) "
                       "FROM account_account "
                       "WHERE CAST(code AS TEXT) "
                       "LIKE '" + base_code + "%'")
            max_code = cr.fetchall()[0][0]

            str_pad = 10
            max_code = max_code.ljust(str_pad, '0')
            max_code = str(int(max_code) + 1)
            max_code = max_code.rjust(str_pad, '0')

        return max_code
