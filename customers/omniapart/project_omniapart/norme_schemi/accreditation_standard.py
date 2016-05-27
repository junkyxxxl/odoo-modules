# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, orm


class accreditation_standard(orm.Model):

    _name = "accreditation.standard"

    _columns = {
        'name': fields.char('Name',
                            size=64),
        'description': fields.text('Description'),
        'schema_ids': fields.many2many('accreditation.schema',
                                       id1='standard_id',
                                       id2='schema_id',
                                       string='Schemi'),
        }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for ap in self.browse(cr, uid, ids):
            descr = ("%s") % (ap.name)
            res.append((ap.id, descr))
        return res
