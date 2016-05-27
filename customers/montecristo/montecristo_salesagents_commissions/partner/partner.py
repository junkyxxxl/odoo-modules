# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp import tools, api


class res_partner(orm.Model):

    _inherit = "res.partner"

    _track = {
        'active': {
            'montecristo_salesagents_commissions.partner_new': lambda self, cr, uid, obj, ctx=None: obj['active'] == True,
        },
    }

    def _check_vat(self, cr, uid, ids, context=None):
        for partner in self.browse(cr, uid, ids, context=context):
            if partner.vat and not partner.force_vat:
                domain = [('vat','like',partner.vat),('id','!=',partner.id)]
                if partner.parent_id:
                    domain.append(('id','!=',partner.parent_id.id))
                    domain.append(('id','not in',list(partner.parent_id.child_ids.ids)))
                if partner.child_ids:
                    domain.append(('id','not in',partner.child_ids.ids))                    
                check = self.search(cr, uid, domain)
                if check:
                    return False
        return True
    
    def _check_cc(self, cr, uid, ids, context=None):
        for partner in self.browse(cr, uid, ids, context=context):
            if partner.vat and partner.country_id and partner.country_id.code:
                if partner.vat[0:2].upper() != partner.country_id.code.upper():
                    return False
        return True    

    def _get_is_current_salesagent(self, cr, uid, ids=None, field_name=None, arg=None, context=None):
        res = {}
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        if isinstance(ids, list):
            res[ids[0]] = salesagent
            return res
        return salesagent

    _columns = {
        'second_salesagent_for_customer_id': fields.many2one('res.partner', 'Subagente'),                
        'subagent_commission_reduction' : fields.float('Percentuale abbattimento subagente %'),
        'subagent_product_commission_reduction' : fields.one2many('partner.product_commission', 'partner_id', 'Percentuale abbattimento subagente per prodotto %'),
        'subagent_category_commission_reduction' : fields.one2many('partner.product_category_commission', 'partner_id', 'Percentuale abbattimento subagente per categoria %'),
        'is_current_salesagent' : fields.function(_get_is_current_salesagent, string="Agente", type="boolean"),
        'force_vat': fields.boolean('Forza P.IVA Doppia'),
    }
    
    @api.model
    def create(self, values):
        salesagent = self.pool.get('res.users').browse(self._cr,self._uid,self._uid).salesagent
        if salesagent:
            if not self._context.get('mail_create_nosubscribe'):
                message_follower_ids = values.get('message_follower_ids') or []  # webclient can send None or False
                if 'country_id' in values:
                    if self.pool.get('res.country').browse(self._cr, self._uid, values['country_id']).code == 'IT':
                        pids = self.pool.get('res.users').search(self._cr,self._uid,[('login','in',['lpredellini','gcimbri','glami'])])
                    else:
                        pids = self.pool.get('res.users').search(self._cr,self._uid,[('login','in',['lpredellini','gcimbri','rguidati'])])
                for pid in pids:
                    t_pid = self.pool.get('res.users').browse(self._cr,self._uid,pid).partner_id.id
                    message_follower_ids.append([4, t_pid])
                values['message_follower_ids'] = message_follower_ids
                
        return super(res_partner,self).create(values)  

    '''
    def _get_category_id(self, cr, uid, context=None):
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        if salesagent:
            salepoint = self.pool.get('res.partner.category').search(cr,uid,[('name','=','PUNTO VENDITA')])
            if salepoint:
                return salepoint
        return   
    '''
    
    def _get_salesagent_for_customer_id(self, cr, uid, context=None):
        salesagent = self.pool.get('res.users').browse(cr,uid,uid).salesagent
        if salesagent:
            return self.pool.get('res.users').browse(cr,uid,uid).partner_id
        return    
    
    def onchange_salesagent_for_customer_id(self, cr, uid, context=None):
        values = {}
        salesagent_obj = self.pool.get('res.users').browse(cr,uid,uid)
        salesagent = salesagent_obj.salesagent
        if salesagent and salesagent_obj.property_product_pricelist:
            values['property_product_pricelist'] = salesagent_obj.property_product_pricelist
        return {'value': values}
    
    
    _defaults = {
                 'salesagent_for_customer_id': _get_salesagent_for_customer_id,
                 'is_current_salesagent': _get_is_current_salesagent,
                 #'category_id': _get_category_id,
                 'is_company': False,
                 'force_vat': False,
    }
    
    _constraints = [(_check_cc, 'Invalid VAT.', ['vat','country_id']),
                    (_check_vat, 'The system already contains another partner with the specified VAT', ['vat'])
                    ]    