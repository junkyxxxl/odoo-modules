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
from datetime import datetime, date, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class wizard_vat_registry(orm.TransientModel):

    _name = "wizard.vat.registry"

    def _get_period(self, cr, uid, context=None):
        ctx = dict(context or {}, account_period_prefer_normal=True)
        period_ids = self.pool.get('account.period').find(cr, uid, context=ctx)
        return period_ids

    _columns = {
        'company_id': fields.many2one('res.company', 
                                      'Company', 
                                      required=True),        
        'period_ids': fields.many2many('account.period',
                                       'registro_iva_periods_rel',
                                       'period_id',
                                       'registro_id',
                                       'Periodi',
                                       help='Select periods you want retrieve documents from',
                                       required=True),
        'tax_sign': fields.float('Segno Importi Tasse',
            help="Use -1 you have negative tax amounts and you want to print them as positive"),
        'message': fields.char('Messaggio', size=64,
                                       readonly=True),
        'fiscal_page_base': fields.integer('Ultima Pagina Stampata',
                                       required=True),
        'iva_registry_id': fields.many2one('vat.registries.isa',
                                       'Registro',
                                       required=True),
        'padding': fields.integer('Padding', 
                                  require=True)
        }

    _defaults = {
        'period_ids': _get_period,
        'tax_sign': 1.0,
        'fiscal_page_base': 0,
        'padding':0,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, context=c),        
        }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        if context is None:
            context = {}
        ctx = {}
        for item in context.items():
            ctx[item[0]] = item[1]
        ctx['company_id'] = company_id
        res = {'value': {}}

        if not company_id:
            return res
        
        res['value'].update({'period_ids': self._get_period(cr, uid, context=ctx)})        
        return res

    def print_registro(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids)[0]
        move_obj = self.pool.get('account.move')
        obj_model_data = self.pool.get('ir.model.data')

        journal_obj = self.pool.get('account.journal')
        t_iva_registry_id = wizard.iva_registry_id
        t_journal_ids = journal_obj.search(cr, uid,
                                    [('iva_registry_id', '=', t_iva_registry_id.id)])

        t_layout_type = wizard.iva_registry_id.layout_type
        if not t_layout_type:
            raise orm.except_orm(_('Error'), _('Nessun Layout Stampa definito per questo Registro.'))

        if isinstance(t_journal_ids, (int, long)):
            t_journal_ids = [t_journal_ids]
        move_ids = move_obj.search(cr, uid, [
            ('journal_id', 'in', [j for j in t_journal_ids]),
            ('period_id', 'in', [p.id for p in wizard.period_ids]),
            ('state', '=', 'posted'),
            ], order='date, name')
        if not move_ids:
            self.write(cr, uid,  ids, {'message': _('No documents found in the current selection')})
            model_data_ids = obj_model_data.search(cr, uid, [('model','=','ir.ui.view'), ('name','=','wizard_vat_registry')])
            resource_id = obj_model_data.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
            return {
                'name': _('No documents'),
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.vat.registry',
                'views': [(resource_id,'form')],
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

        if context.get('final', False):
            first_protocol = context.get('last_protocol') + 1
            for i in range(len(move_ids)):
                move_obj.write(cr, uid, move_ids[i], {'protocol_number':str(first_protocol+i)})
            
        datas = {'ids': move_ids}
        datas['model'] = 'account.move'
        datas['fiscal_page_base'] = wizard.fiscal_page_base
        datas['period_ids'] = [p.id for p in wizard.period_ids]
        datas['layout'] = t_layout_type
        datas['tax_sign'] = wizard['tax_sign']
        datas['iva_registry_id'] = wizard['iva_registry_id'].id
        datas['padding'] = wizard['padding']
        datas['company_id'] = wizard['company_id'].id
        
        if 'final' in context:
            datas['final'] = context['final']
        else:
            datas['final'] = False
        
        res= {
            'type': 'ir.actions.report.xml',
            'datas': datas,
        }
        if t_layout_type == 'customer':
            res['report_name'] = 'vat_registry_sale_webkit'
        elif t_layout_type == 'supplier':
            res['report_name'] = 'vat_registry_purchase_webkit'
        elif t_layout_type == 'corrispettivi':
            res['report_name'] = 'vat_registry_corrispettivi_webkit'
        return res

    def print_registro_final(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        wizard = self.browse(cr, uid, ids)[0]
        obj_model_data = self.pool.get('ir.model.data')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        journal_year_rel_obj = self.pool.get('account.journal.fiscalyear.related')

        iva_registry_id = wizard.iva_registry_id

        t_journal_ids = journal_obj.search(cr, uid,
                                    [('iva_registry_id', '=', iva_registry_id.id)])


        period_ids = wizard.period_ids        
        today_date = date.today()
        
        for p in period_ids:
            #CONTROLLA CHE TRA I PERIODI NON CI SIA QUELLO IN CORSO 
            str_date_stop = period_obj.read(cr,uid,[p.id],['date_stop'])[0]['date_stop']
            date_stop = datetime.strptime(str_date_stop, DF).date() 
            if date_stop > today_date:
                self.write(cr, uid,  ids, {'message': _('You can not print a VAT register of the current period!')})
                model_data_ids = obj_model_data.search(cr, uid, [('model','=','ir.ui.view'), ('name','=','wizard_vat_registry')])
                resource_id = obj_model_data.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
                return {
                    'name': _('No documents'),
                    'res_id': ids[0],
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'wizard.vat.registry',
                    'views': [(resource_id,'form')],
                    'context': context,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        
        #CONTROLLA CHE TRA I PERIODI NON CI SIANO BUCHI
        test_period_ids = period_obj.search(cr, uid, [('id','in',period_ids.ids)],order='date_start', context=context)
        
        for i in range(len(test_period_ids)-1):
            period_1 = period_obj.browse(cr, uid, test_period_ids[i], context=context)
            period_2 = period_obj.browse(cr, uid, test_period_ids[i+1], context=context)
            
            error_id = period_obj.search(cr, uid, [('date_start','>=',period_1.date_stop),('date_stop','<=',period_2.date_start)])
            if error_id:
                self.write(cr, uid,  ids, {'message': _('In your period selection there are holes.')})
                model_data_ids = obj_model_data.search(cr, uid, [('model','=','ir.ui.view'), ('name','=','wizard_vat_registry')])
                resource_id = obj_model_data.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
                return {
                    'name': _('No documents'),
                    'res_id': ids[0],
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'wizard.vat.registry',
                    'views': [(resource_id,'form')],
                    'context': context,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }                

        #CONTROLLA CHE I PERIODI SELEZIONATI SIANO IMMEDIATAMENTE SUCCESSIVI ALL'ULTIMO PERIODO STAMPATO
        min = period_ids[0]
        for p in period_ids:
            if p.date_start < min.date_start:
                min = p           
        
        last_protocol = 0
        last_printed = journal_year_rel_obj.search(cr,uid,[('iva_registry_id','=',iva_registry_id.id),('fiscalyear_id','=',p.fiscalyear_id.id)])
        if last_printed and last_printed[0]:
            last_printed = journal_year_rel_obj.browse(cr,uid,last_printed[0])
            last_protocol = last_printed[0].last_printed_protocol
            last_printed = last_printed[0].last_print_date
            if last_printed > min.date_start:
                self.write(cr, uid,  ids, {'message': _('One of the selected periods was already printed as final!')})
                model_data_ids = obj_model_data.search(cr, uid, [('model','=','ir.ui.view'), ('name','=','wizard_vat_registry')])
                resource_id = obj_model_data.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
                return {
                    'name': _('No documents'),
                    'res_id': ids[0],
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'wizard.vat.registry',
                    'views': [(resource_id,'form')],
                    'context': context,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }            
            for period in p.fiscalyear_id.period_ids:
                if period.date_start > last_printed and period.date_stop < min.date_start:
                    self.write(cr, uid,  ids, {'message': _('You have to print the previous periods before!')})
                    model_data_ids = obj_model_data.search(cr, uid, [('model','=','ir.ui.view'), ('name','=','wizard_vat_registry')])
                    resource_id = obj_model_data.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
                    return {
                        'name': _('No documents'),
                        'res_id': ids[0],
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'wizard.vat.registry',
                        'views': [(resource_id,'form')],
                        'context': context,
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }  

        context.update({'final': True, 'last_protocol': last_protocol})
        
                
        #RICHIAMA LA STAMPA    
        res = self.print_registro(cr, uid, ids, context)
        
        #SE NELLA STAMPA NON CI SONO ERRORI
        if 'datas' in res:
            for p in period_ids:
              
                v_iva = iva_registry_id.id
                v_year = period_obj.read(cr,uid,[p.id],['fiscalyear_id'])[0]['fiscalyear_id'][0],               
                str_date_stop = period_obj.read(cr,uid,[p.id],['date_stop'])[0]['date_stop']
                date_stop = datetime.strptime(str_date_stop, DF).date() 
                rel_ids = journal_year_rel_obj.search(cr,uid,[('iva_registry_id','=',v_iva),('fiscalyear_id','=',v_year)])
                
                #CALCOLA ED ASSEGNA IL VALORE DELL'ULTIMO PROTOCOL NUMBER STAMPATO
                cr.execute( """
                                SELECT protocol_number
                                FROM account_move
                                WHERE 
                                    period_id = %s AND
                                    journal_id in %s
                            """, (p.id,tuple(t_journal_ids),)
                            )
                p_numbers = cr.fetchall()
                numbers = []
                for number in p_numbers:
                    numbers.append(int(number[0]))
                if len(numbers)> 0:
                    v_pnumb = max(numbers)
                else:
                    v_pnumb = 0
                    
                #SE SONO GIA' STATI STAMPATI PERIODI PRECEDENTI DELLO STESSO FISCALYEAR, ESEGUE AGGIORNA IL RECORD
                #SE SONO GIA' STATI STAMPATI PERIODI SUCCESSIVI DELLO STESSO FISCALYEAR, NON MODIFICA IL RECORD
                if len(rel_ids)>0:
                    rel_id = rel_ids[0]
                    t_relation = journal_year_rel_obj.read(cr,uid,[rel_id],['last_print_date','last_printed_protocol'])
                    t_str_date_stop = t_relation[0]['last_print_date']
                    t_pnumb = t_relation[0]['last_printed_protocol']
                    t_date_stop = datetime.strptime(t_str_date_stop, DF).date()
                    if t_date_stop < date_stop:
                        journal_year_rel_obj.write(cr,uid,[rel_id],{'last_print_date':date_stop,})
                        if v_pnumb > t_pnumb:
                            journal_year_rel_obj.write(cr,uid,[rel_id],{'last_printed_protocol':v_pnumb,})                        
                #SE NON SONO STATI MAI STAMPATI PERIODI DELLO STESSO FISCALYEAR, CREA UN NUOVO RECORD
                else:
                    values = {
                                'iva_registry_id': v_iva,
                                'fiscalyear_id': v_year,
                                'last_print_date': date_stop,
                                'last_printed_protocol': v_pnumb, 
                             }
                    journal_year_rel_obj.create(cr,uid,values)
        return res


    def onchange_iva_registry_id(self, cr, uid, ids,
                                          iva_registry_id,
                                          context=None):
        if context is None:
            context = {}
        res={}
        warning = {}
        if iva_registry_id:
            registry_obj = self.pool.get('vat.registries.isa')
            registry_data = registry_obj.browse(cr, uid,
                                        iva_registry_id,
                                        context)
            if registry_data:
                if registry_data.sequence_iva_registry_id.prefix:
                    warning = {
                               'title': _('Warning!'),
                               'message': _('This sequence is not allowed because it contains a prefix')
                               }
                    return {'value': {},
                            'warning': warning,
                             }
                if registry_data.sequence_iva_registry_id.suffix:
                    warning = {
                               'title': _('Warning!'),
                               'message': _('This sequence is not allowed because it contains a suffix')
                               }
                    return {'value': {},
                            'warning': warning,
                             }

            if registry_data and registry_data.layout_type:
                if registry_data.layout_type == 'supplier':
                    res['value'] = {'tax_sign': -1}
                else:
                    res['value'] = {'tax_sign': 1}
                return res

        return {'value': {},
                'warning': warning,
                 }