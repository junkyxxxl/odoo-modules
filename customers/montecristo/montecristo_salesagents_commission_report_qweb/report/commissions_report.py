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

import time
from openerp.report import report_sxw
from openerp.addons.salesagent_commissions_report_qweb.report import commissions_report
from openerp.osv import osv

class montecristo_commissions_report_parser(commissions_report.commissions_report_parser):

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        if context is None:
            context = {}
        super(montecristo_commissions_report_parser,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_salesagents':self._get_salesagents,
            'get_lines':self._get_lines,
            'get_totals':self._get_totals,
        })
        self.context = context

    def _carriage_returns(self, text):
          if text:
             text.replace('\n', '<br />')
             return text 
    
    def _get_salesagents(self, objects):        
        salesagent_list = []
        
        line_obj = self.pool.get('account.invoice.line')
        
        for object in objects:
            line = line_obj.browse(self.cr, self.uid,object)
            if line.salesagent_id and line.salesagent_id.id > 0:
                salesagent_list.append(line.salesagent_id)
            if line.salesagent_id_base and line.salesagent_id_base.id > 0:
                salesagent_list.append(line.salesagent_id_base)

        salesagent_list = list(set(salesagent_list))
        return salesagent_list

    def _get_lines(self, ids):
        line_obj = self.pool.get('account.invoice.line')
        lines = []
        for id in ids:
            t_line = line_obj.browse(self.cr, self.uid, id)
            lines.append(t_line)
        return lines

    def _get_totals(self, ids, agent):
        
        res = []
        tot_paid = 0.0
        tot_commission = 0.0
        tot_amount_untaxed_commission = 0.0
        
        for object in self._get_lines(ids):
            if agent.id == object.salesagent_id.id or agent.id == object.salesagent_id_base.id:
                tot_amount_untaxed_commission = tot_amount_untaxed_commission + object.price_subtotal
                if agent.id == object.salesagent_id.id:
                    tot_paid = tot_paid + object.paid_commission_value
                    tot_commission = tot_commission + object.commission
                else:
                    tot_paid = tot_paid + object.paid_commission_value_base
                    tot_commission = tot_commission + object.commission_base
                    
        res.append(tot_amount_untaxed_commission)
        res.append(tot_commission)
        res.append(tot_paid)
        return res                
    
    def _check_parity(self, n):
        if n % 2 == 0:
            return True
        else:
            return False
        
    def _check_disparity(self, n):
        if n % 2 == 0:
            return False
        else:
            return True        
    
class report_invoice_qweb(osv.AbstractModel):
    _name = 'report.salesagent_commissions_report_qweb.report_commissions_qweb'
    _inherit = 'report.abstract_report'
    _template = 'salesagent_commissions_report_qweb.report_commissions_qweb'
    _wrapped_report_class = montecristo_commissions_report_parser
    
