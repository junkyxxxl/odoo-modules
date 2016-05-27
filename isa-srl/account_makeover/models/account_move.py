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


class account_move_makeover(orm.Model):

    _inherit = 'account.move'

    _columns = {
        'protocol_number': fields.char('Numero Protocollo',
                                     size=64,
                                     readonly=True),
        'document_number': fields.char('Document Number',
                                     size=64),
        'document_date': fields.date('Document Date',
                                     states={'posted':[('readonly', True)]},
                                     select=True),
    }

    _defaults = {
        'document_date': fields.date.context_today,
    }

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        result = super(account_move_makeover, self).post(cr, uid, ids, context)

        if result:
            for move in self.browse(cr, uid, ids, context=context):
                if not move.protocol_number and move.journal_id.iva_registry_id:
                    invoice_obj = self.pool.get('account.invoice')
                    invoice_ids = invoice_obj.search(cr, uid,
                                                [('move_id', '=', move.id)])
                    if not invoice_ids:
                        obj_seq = self.pool.get('ir.sequence')
                        t_seq_id = move.journal_id.iva_registry_id.sequence_iva_registry_id.id
                        number_next = obj_seq.next_by_id(cr, uid, t_seq_id)

                        self.write(cr, uid, [move.id],
                                   {'protocol_number': number_next})
                    else:
                        for invoice_data in invoice_obj.browse(cr, uid, invoice_ids, context=context):
                            if invoice_data.force_protocol_number:
                                self.write(cr, uid, [move.id],
                                           {'protocol_number': str(invoice_data.force_protocol_number)})
                            else:
                                obj_seq = self.pool.get('ir.sequence')
                                t_seq_id = move.journal_id.iva_registry_id.sequence_iva_registry_id.id
                                number_next = obj_seq.next_by_id(cr, uid, t_seq_id)

                                self.write(cr, uid, [move.id],
                                           {'protocol_number': number_next})
        return result
