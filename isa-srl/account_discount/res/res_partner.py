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
import openerp.addons.decimal_precision as dp

class res_partner_discount(orm.Model):
    _name = 'partner.discount'
    _description = 'Sconto Globale'
    _order = 'sequence ASC'    
    _columns= {
                'name': fields.many2one('account.discount.type', string='Nome', required = True),
                'application': fields.selection([('partner','Cliente'),('payment','Termine di Pagamento'),('general','Generale')], string='Applicazione', required=True),
                'type': fields.selection([('perc','%'),('fisso','Fisso')], string='Tipo', required=True),
                'sequence': fields.integer('Sequence'),
                'value': fields.float('Valore'),
                'partner_id': fields.many2one('res.partner', string='Partner'),
    }    
    _defaults={
               'sequence':0,
               'type':'perc',
               'application':'partner',
    }

class res_partner_with_discount(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'global_discount_lines': fields.one2many('partner.discount', 'partner_id', string='Sconti Globali'),              
    }
