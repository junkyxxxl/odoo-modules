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


class account_journal_fiscalyear_related(orm.Model):
    _name = 'account.journal.fiscalyear.related'

    _columns = {
        'iva_registry_id': fields.many2one('account.journal',
                                       'Sezionale di riferimento',
                                       required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear',
                                       'Anno fiscale di riferimento',
                                       required=True),
        'last_print_date':  fields.date('Date last print'),
        'last_printed_protocol': fields.integer('Last printed protocol number'),
    }

    
