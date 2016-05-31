# -*- coding: utf-8 -*-
###############################################################################
#
##############################################################################

from openerp.osv import orm, fields

class due_list(orm.TransientModel):
    _name = 'account.due.list.report'
    _description = 'Print Account Due List Report'
    
    def _get_partner_ids(self, cr, uid, context=None):
        res = False
        if context.get('active_model', False) == 'res.partner' and context.get('active_ids', False):
            res = context['active_ids']
        return res
    
    _columns = {
        'company_id': fields.many2one('res.company', 
                                      'Company', 
                                      required=True), 
        'date_maturity': fields.date('Data Scadenza',
                                      required=True),
        'partner_ids': fields.many2many('res.partner', string='Partner'),
        'mode': fields.selection([('matured', 'Scaduto'),
                                   ('tomature', 'A Scadere')],
                                  string='Modalità',
                                  required=True),
        'print_customers': fields.boolean('All Customers'),
        'print_suppliers': fields.boolean('All Suppliers'),
        'type': fields.selection([('debit','Cliente'),('credit','Fornitore')],'Tipo Scadenza'),
        'all_partner': fields.boolean('Tutti i partner',default = True)
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, context=c),        
        'date_maturity': fields.date.context_today,
        'partner_ids' : _get_partner_ids,
        'mode':'matured',
    }

    def print_report_pdf(self, cr, uid, ids, context=None):
        datas = {
             'ids': [],
             'model': 'account.move.line',
             'form': self.read(cr, uid, ids)[0]
        }
        print datas
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'due_list_pdf',
            'datas':datas,
        }
