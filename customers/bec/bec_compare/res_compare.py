# -*- coding: utf-8 -*-

import datetime
import time

import openerp
from openerp.osv import osv, fields
from openerp.tools.translate import _

class res_partner(osv.osv):
    _description = 'Add relation bec_dealer_ids'
    _name = "res.partner"
    _inherit = "res.partner"

    _columns = {
        'bec_compare_ids': fields.one2many('res.compare.partner', 'parent_id', 'Comparison Related'),
    }

res_partner()

class res_compare_partner(osv.osv):
    _description = 'Compare Partner'
    _name = "res.compare.partner"
    _rec_name = "parent_id"

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['parent_id','board_id'], context=context)
        res = []
        for record in reads:
            name = record['parent_id'][1]
#            if record['board_id']:
#                name = name +' [' + record['board_id'][1] + ']'
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def create(self, cr, uid, vals, context=None):

        vals['state'] = ''

        submit=True
        if not 'data_submit' in vals.keys():
            submit = False
        elif not vals['data_submit']:
            submit = False

        received=True
        if not 'data_received' in vals.keys():
            received = False
        elif not vals['data_received']:
            received = False

        if submit:
            vals['state'] = 'sent'

        if submit and received:
            vals['state'] = 'received'

        ids = super(res_compare_partner, self).create(cr, uid, vals, context=context)

        return ids

    def write(self, cr, uid, ids, vals, context=None):

        vals['state'] = ''

        # controlla le date di invio/ricezione aggiorna lo stato
        for compare in self.browse(cr, uid, ids, context=context):

            submit=False
            if vals.get('data_submit') or vals.get('data_submit') is not None:
                submit=vals.get('data_submit')
            else:
                submit=compare.data_submit

            received=False
            if vals.get('data_received') or vals.get('data_received') is not None:
                received=vals.get('data_received')
            else:
                received=compare.data_received

        if submit:
            vals['state'] = 'sent'

        if submit and received:
            vals['state'] = 'received'


        result = super(res_compare_partner,self).write(cr, uid, ids, vals, context=context)

        return result


    _columns = {
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'parent_id': fields.many2one('res.partner', 'Company', required=True, ondelete='cascade'),
        'phone': fields.related('parent_id','phone', type="char", size=64, relation="res.partner", string="Phone", readonly=True, store=False),
        'email': fields.related('parent_id','email', type="char", size=240, relation="res.partner", string="Email", readonly=True, store=False),
        'ref': fields.related('parent_id','ref', type="char", size=64, relation="res.partner", string="Reference", store=False),
        'data_submit': fields.date('Submit Date', help='Submit date comparison.'),
        'data_received': fields.date('Date Received', help='Received date comparison.'),
        'board_id': fields.many2one('res.compare.board', 'Comparison Related', required=True, ondelete='cascade'),
        'state': fields.selection([('sent', 'Sent'), ('received', 'Received')], 'Status'),
    }

    _defaults ={
        'data_submit': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'sent',
    }

    _order = "board_id desc, parent_id, data_submit desc, data_received desc"

res_compare_partner()

class res_compare_board(osv.osv):

    def bnumber_get(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        if context.get('compare_board_display') == 'short':
            return super(res_compare_board, self).bnumber_get(cr, uid, ids, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['number', 'year'], context=context)
        res = []
        for record in reads:
            number = record['number']
            if record['year']:
                number = number + ' / ' + record['year']
            res.append((record['id'], number))
        return res

    def _bnumber_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.bnumber_get(cr, uid, ids, context=context)
        return dict(res)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('compare_board_display') == 'short':
            return super(res_compare_board, self).name_get(cr, uid, ids, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'bnumber'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['bnumber']:
                name = record['bnumber'] + ' | ' + name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _description = 'Compare Board'
    _name = "res.compare.board"
    _rec_name = "name"
#many2many(
    _columns = {
        'partner_ids': fields.one2many('res.compare.partner', 'board_id', 'Related Company'),
        'name': fields.char('Name', size=128, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
        'number': fields.char('Number', size=2, required=True, help='Max 2 char, example 8'),
        'year': fields.char('Year', size=4, required=True, help='Max 4 char, example 2014'),
        'bnumber': fields.function(_bnumber_get_fnc, type="char", readonly=True, string='Serial'),
    }

res_compare_board()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
