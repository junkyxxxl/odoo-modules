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


class sale_order_montecristo(osv.osv):
    _inherit = "sale.order"
    
    _track = {
        'state': {
            'montecristo_salesagents_commissions.sale_order_new': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['draft'],
        },
    }
    
    def _get_salesagent(self, cr, uid, ids=None, field_name=None, arg=None, context=None):
        res = {}
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        if isinstance(ids, list):
            res[ids[0]] = salesagent
            return res
        return salesagent
    
    _columns = {
                'salesagent': fields.function(_get_salesagent, string="Agente", type="boolean"),
                'confirmed': fields.boolean('Approved'),
    }

    _defaults = {
                'salesagent': _get_salesagent,
    }

    def _check_approved(self, cr, uid, ids, context=None):
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        confirmed = self.browse(cr,uid,ids,context=context).confirmed
        if salesagent and confirmed:
            return False
        return True

    _constraints = [
        (_check_approved, 'Il documento è già stato approvato, non sono ammesse ulteriori modifiche da parte degli agenti.', 
         ['salesagent','confirmed','delivery_date','partner_id','order_line']),
    ]    

    def onchange_partner_id(self, cr, uid, ids, partner_id, season=None, salesagent_id=None, context=None):
        res = super(sale_order_montecristo, self).onchange_partner_id(cr, uid, ids, partner_id, season=season, salesagent_id=salesagent_id, context=context)        
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        if salesagent and partner_id:
            partner = self.pool.get('res.partner').read(cr, uid, partner_id, ['salesagent_for_customer_id','second_salesagent_for_customer_id'])
            agent_id = self.pool.get('res.users').browse(cr,uid,uid,context=context).partner_id and self.pool.get('res.users').browse(cr,uid,uid,context=context).partner_id.id
            if agent_id and (agent_id == partner['salesagent_for_customer_id'][0] or agent_id == partner['second_salesagent_for_customer_id'][0]):
                if 'value' not in res:
                    if agent_id and 'value' not in res:
                        return {'value': {'salesagent_id': agent_id,
                                          }}
                    return {'value': {'salesagent_id': None,
                                          }}
                res['value']['salesagent_id'] = agent_id                      
        return res
    
    def create(self, cr, uid, values, context=None):
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        if salesagent:
            message_follower_ids = values.get('message_follower_ids') or []  # webclient can send None or False
            if 'partner_id' in values:
                if self.pool.get('res.partner').browse(cr, uid, values['partner_id']).country_id and self.pool.get('res.partner').browse(cr, uid, values['partner_id']).country_id.code == 'IT':
                    pids = self.pool.get('res.users').search(cr,uid,[('login','in',['glami'])])
                else:
                    pids = self.pool.get('res.users').search(cr,uid,[('login','in',['rguidati'])])
            for pid in pids:
                t_pid = self.pool.get('res.users').browse(cr,uid,pid).partner_id.id
                message_follower_ids.append([4, t_pid])
            values['message_follower_ids'] = message_follower_ids
        return super(sale_order_montecristo,self).create(cr,uid,values,context=context) 
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        # fetch the partner's id and subscribe the partner to the sale order
        assert len(ids) == 1
        self.write(cr, uid, ids[0], {'confirmed':True})
        document = self.browse(cr, uid, ids[0], context=context)
        partner = document.partner_id
        remove = False
        if partner not in document.message_follower_ids:
            remove = True
        
        res = super(sale_order_montecristo, self).action_button_confirm(cr, uid, ids, context=context)
        
        if partner in document.message_follower_ids and remove:
            self.message_unsubscribe(cr, uid, ids, [partner.id], context=context)
        return res