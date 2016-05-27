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

from openerp.osv import fields, orm


class uffici(orm.Model):
    _name = 'doclite.uffici'
    _description = 'Doclite Uffici'
    _columns = {        
        'codice':fields.char('Code', size=100,
                                   translate=True,
                                   help='Code',
                                   select=True),
        'descrizione': fields.char('Description',
                                   size=50,
                                   help='Description',
                                   translate=True,
                                   required=True,
                                   select=True),
        'active': fields.boolean('Active') 
    }

    _defaults = {
        'active': True,
    }

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for off in self.browse(cr, uid, ids):
            descr = ("[%s] %s") % (off.codice,
                                   off.descrizione)
            res.append((off.id, descr))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                                                context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}

        req_ids = self.search(cr, uid, args + 
                              ['|',
                               ('codice', operator, name),
                               ('descrizione', operator, name)],
                              limit=limit,
                              context=context)
        return self.name_get(cr, uid, req_ids, context=context)
