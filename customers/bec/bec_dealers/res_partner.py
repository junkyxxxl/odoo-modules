# -*- coding: utf-8 -*-
# Original file: /usr/lib/pymodules/python2.7/openerp/addons/base/res/res_partner.py

import openerp
from openerp.osv import osv, fields
from openerp.tools.translate import _

class res_partner(osv.osv):
    _description = 'Add relation bec_dealer_ids'
    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'bec_dealer_ids': fields.one2many('res.partner.dealer', 'bec_dealer_id', 'Dealers'),
        'bec_manufacturer_ids': fields.one2many('res.partner.dealer', 'bec_manufacturer_id', 'Manufacturer'), 
    }

res_partner()

class res_partner_dealer(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['bec_dealer_id','bec_manufacturer_id'], context=context)
        res = []
        for record in reads:
            name = record['bec_dealer_id'][1]
#            if record['bec_manufacturer_id']:
#                name = name +' [' + record['bec_manufacturer_id'][1] + ']'
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _description = 'Partner Dealer'
    _name = "res.partner.dealer"
    _rec_name = "bec_dealer_id"

    _columns = {
        #'type_relation': fields.selection([('distributore', 'Distributore')], 'Relazione', required=True, size=64, translate=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'bec_dealer_id': fields.many2one('res.partner', 'Distributed by', required=True, ondelete='cascade'),
        'bec_manufacturer_id': fields.many2one('res.partner', 'Distributor of', required=True, ondelete='cascade'),
        'bec_dealer_zip': fields.related('bec_dealer_id','zip', type="char", size=24, relation="res.partner", string="Zip", readonly=True, store=False),
        'bec_dealer_city': fields.related('bec_dealer_id','city', type="char", size=128, relation="res.partner", string="City", readonly=True, store=False),
        'bec_dealer_province': fields.related('bec_dealer_id','province', type="many2one", relation="res.province", string="Province", readonly=True, store=False),
        'bec_dealer_region': fields.related('bec_dealer_id','region', type="many2one", relation="res.region", string="Region", readonly=True, store=False),
        'bec_dealer_country_id': fields.related('bec_dealer_id','country_id', type="many2one", relation="res.country", string="Country", readonly=True, store=False),
    }

res_partner_dealer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
