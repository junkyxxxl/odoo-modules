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


from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from math import ceil
import openerp.addons.decimal_precision as dp

class wizard_search_invoice(osv.osv_memory):
    _name = "wizard.search.invoice"
    _description = "Search Invoice"

    _columns = {
        'partner_id': fields.many2one('res.partner', string='Partner'),
        'analytic_id': fields.many2one('account.analytic.account', string='Contract'),
        'date_to': fields.date('To Date'),
        'date_from': fields.date('From Date'),
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = {'domain':{}}
        if partner_id:
            res['domain'].update({'analytic_id':[('partner_id','=',partner_id)],})
        else:
            res['domain'].update({'analytic_id':None})
        return res

    def search_invoice(self, cr, uid, ids, context=None):
        
        partner_id = self.browse(cr, uid, ids)[0].partner_id
        analytic_id = self.browse(cr, uid, ids)[0].analytic_id
        date_from = self.browse(cr, uid, ids)[0].date_from
        date_to = self.browse(cr, uid, ids)[0].date_to
        
        sql_qry = 'SELECT DISTINCT inv.id FROM account_invoice AS inv, account_invoice_line AS line WHERE line.invoice_id = inv.id AND inv.state NOT IN (\'paid\',\'cancel\') AND line.account_analytic_id = ' + str(analytic_id.id) 
        
        if date_from:
            sql_qry = sql_qry + ' AND inv.date_invoice >= \'' + date_from + '\''
            
        if date_to:
            sql_qry = sql_qry + ' AND inv.date_invoice <= \'' + date_to + '\''
        
        cr.execute(sql_qry,())
        
        t_inv_ids = cr.fetchall()
        inv_ids = []
        for item in t_inv_ids:
            inv_ids.append(item[0])


        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account',
                                              'invoice_tree')
        view_id = result and result[1] or False

        return {'domain': "[('id','in', ["+','.join(map(str,inv_ids))+"])]",
                'name': _("Fatture legate al contratto \""+analytic_id.name+"\""),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'context': context,
                'views': [(view_id,'tree'),(False,'form')],
                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    