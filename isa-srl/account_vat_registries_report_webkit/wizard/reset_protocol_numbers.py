# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
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
from openerp.tools.translate import _
from openerp.osv.osv import except_osv


class wizard_reset_protocol_numbers(orm.TransientModel):

    _name = "wizard.reset.protocol.numbers"

    _columns = {
        'journal_id': fields.many2one('account.journal',
                                       'Sezionale di riferimento',
                                       required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear',
                                       'Anno fiscale di riferimento',
                                       required=True),
        }

    
    def reset_protocol_numbers(self, cr, uid, ids, context=None):
        
        if(not ids[0]):
            raise except_osv(_('Error!'), _('Operation Failed !'))
        wiz_obj = self.browse(cr,uid,ids[0])
        if (not wiz_obj or not wiz_obj.journal_id or not wiz_obj.fiscalyear_id or not wiz_obj.journal_id.id or not wiz_obj.fiscalyear_id.id):
            raise except_osv(_('Error!'), _('Operation Failed !'))
            
        
        fiscalyear_id = wiz_obj.fiscalyear_id.id
        journal_id = wiz_obj.journal_id.id
        
        if fiscalyear_id == False or journal_id == False:
            raise except_osv(_('Error!'), _('Operation Failed !'))
        
        #UPDATE DEI MOVIMENTI
        cr.execute('''
                        UPDATE account_move
                        SET protocol_number=subquery.position+offs.number
                        FROM
                            (
                            SELECT
                                row_number() OVER(ORDER BY mov.protocol_number, mov.id)  AS position,
                                mov.id AS id,
                                (
                                SELECT inv.id
                                FROM account_invoice AS inv
                                WHERE inv.move_id = mov.id
                                ) AS inv_id
                            FROM 
                                account_move as mov, 
                                account_period as per,
                                vat_registries_isa AS vat,
                                account_journal AS jour,
                                account_journal_fiscalyear_related AS rel 
                            WHERE  
                                mov.period_id = per.id AND 
                                per.fiscalyear_id = %s AND 
                                mov.journal_id = %s AND
                                mov.journal_id = jour.id AND
                                jour.iva_registry_id = vat.id AND
                                vat.id = rel.iva_registry_id AND
                                per.fiscalyear_id = rel.fiscalyear_id AND
                                CAST(mov.protocol_number AS integer) > rel.last_printed_protocol
                            ORDER BY 
                                mov.protocol_number, 
                                mov.id
                            ) AS subquery,
                            (
                            SELECT rel.last_printed_protocol AS number
                            FROM 
                                account_journal_fiscalyear_related AS rel,
                                account_journal AS jou
                            WHERE
                                rel.fiscalyear_id = %s AND
                                jou.iva_registry_id = rel.iva_registry_id AND
                                jou.id = %s
                            ) AS offs

                        WHERE 
                            account_move.id = subquery.id                          
                        ''',
                    (fiscalyear_id, journal_id, fiscalyear_id, journal_id))

        #CALCOLO ID E NEXT DELLA SEQUENCE
        cr.execute('''
                        SELECT vat.sequence_iva_registry_id,
                            ( 
                            SELECT COUNT(mov.id)
                            FROM 
                                account_move AS mov, 
                                account_period AS per, 
                                account_journal_fiscalyear_related AS rel
                            WHERE 
                                mov.journal_id = 1 AND 
                                mov.period_id = per.id AND 
                                per.fiscalyear_id = 1 AND
                                mov.journal_id = jou.id AND
                                jou.iva_registry_id = rel.iva_registry_id AND
                                rel.iva_registry_id = vat.id AND
                                CAST(mov.protocol_number AS integer)> rel.last_printed_protocol
                            )+rel.last_printed_protocol AS next_numb
                        FROM 
                            account_journal AS jou, 
                            vat_registries_isa AS vat,
                            account_journal_fiscalyear_related AS rel
                        WHERE 
                            jou.id = 1 AND 
                            jou.iva_registry_id = vat.id AND
                            jou.iva_registry_id = rel.iva_registry_id
                    ''',
                    (journal_id,fiscalyear_id,journal_id))
        
        tmp = cr.fetchall()[0]
        sequence = tmp[0]
        next = tmp[1]+1
        
        #UPDATE DELLA SEQUENCE
        cr.execute('UPDATE ir_sequence SET number_next=%s WHERE id = %s', (next, sequence))
        
        ok_msg = []
        ok_msg.append((_("Operation completed"))) 
        
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_vat_registries_report_webkit',
                                              'post_reset_view')
        view_id = result and result[1] or False
 
        return {
               'name': _("Post Reset"),
               'view_type': 'form',
               'view_mode': 'form',
               'res_model': 'wizard.post.reset',
               'type': 'ir.actions.act_window',
               'view_id': view_id,
               'context': context,
               'target': 'new',
               }