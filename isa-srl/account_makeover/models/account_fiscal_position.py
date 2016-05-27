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

from openerp.osv import orm


class account_fiscal_position(orm.Model):
    _inherit = 'account.fiscal.position'

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        t_company_dict = {}
        t_datas = self.browse(cr, uid, ids)
        for t_data in t_datas:
            if t_data.company_id:
                t_company_dict.update({t_data.company_id.id: True})
            if len(t_company_dict)>1:
                break
        for t_data in t_datas:
            if t_data.company_id and len(t_company_dict)>1:
                descr = ("[%s] %s") % (t_data.company_id.name,
                                       t_data.name)
            else:
                descr = (" %s") % (t_data.name)
            res.append((t_data.id, descr))
        return res
