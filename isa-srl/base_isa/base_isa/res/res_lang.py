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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class res_lang(orm.Model):
    _inherit='res.lang'
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'grouping' in vals and vals['grouping'].find('.')!=-1  :
            raise orm.except_orm(_('Valore non consentito!'), _('Non puoi inserire il carattere "." nel campo "Formato Separatore"'))
        return super(res_lang, self).write(cr, uid, ids, vals, context=context)


