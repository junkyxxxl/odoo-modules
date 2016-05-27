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

from openerp.osv import fields, osv

class res_composizione(osv.osv):
    _name = "res.family"

    _columns = {'name': fields.char('Name', required=True),
                'code': fields.char('Local Code', required=True),
                'type': fields.selection([('family','Famiglia'),
                                          ('subfamily','Sottofamiglia'),
                                          ('subgroup','Sottogruppo'),
                                          ('composition','Composizione'),
                                          ('origin','Origine'),
                                          ('production','Produzione')],
                                         'Classificazione'),
                'date_start':fields.date('Inizio Consegne'),
                'date_end':fields.date('Fine Consegne'),
                'previous_ref':fields.many2one("res.family","Riferimento ad anno precedente",domain="[('type','=','production')]"),
                'current':fields.boolean('Attivo'),
                'category_dates_id':fields.one2many('res.family.category.date','family_id','Group Delivery Informations'),
                }

    def _check_dates(self, cr, uid, ids, context=None):
        end = self.browse(cr,uid,ids,context=context).date_end
        start = self.browse(cr,uid,ids,context=context).date_start
        if  end < start:
            return False
        return True

    _constraints = [
        (_check_dates, 'La data di fine consegne non può essere antecedente alla data di inizio consegne', 
         ['date_start','date_end']),
    ]

class res_family_category_date(osv.osv):
    _name = "res.family.category.date"

    _columns = {
                'family_id': fields.many2one('res.family','Season',domain="[('type','=','production')]"),
                'category_id':fields.many2one('product.category',string='Gruppo',required=True),
                'information':fields.char('Delivery Informations', size=20),
                'begin_date': fields.date('Inizio Consegne'),
                'end_date': fields.date('Fine Consegne'),
                }
