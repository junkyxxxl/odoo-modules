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

from openerp import models, fields, api, exceptions, _
from openerp.osv import orm, fields


class account_journal(orm.Model):
    _inherit = 'account.journal'

    _columns = {
        'check_previous_date':fields.boolean('Controllo data in registrazioni precedenti', help= 'If checked, the entry won\'t be created if the entry date is not coherent with the other registrations in the same journal'),
    }
    
    _defaults= {
        'check_previous_date': True,
    }