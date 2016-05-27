# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp import workflow
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class riba_distinta(orm.Model):
    
    def _get_acceptance_move_ids(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for distinta in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in distinta.line_ids:
                if line.acceptance_move_id and line.acceptance_move_id.id not in move_ids:
                    move_ids.append(line.acceptance_move_id.id)
            res[distinta.id] = move_ids
        return res
    
    def _get_unsolved_move_ids(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for distinta in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in distinta.line_ids:
                if line.unsolved_move_id and line.unsolved_move_id.id not in move_ids:
                    move_ids.append(line.unsolved_move_id.id)
            res[distinta.id] = move_ids
        return res
    
    def _get_payment_ids(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for distinta in self.browse(cr, uid, ids, context=context):
            move_line_ids = []
            for line in distinta.line_ids:
                for payment in line.payment_ids:
                    if payment.id not in move_line_ids:
                        move_line_ids.append(payment.id)
            res[distinta.id] = move_line_ids
        return res

    def _get_distinta(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('riba.distinta.line').browse(cr, uid, ids, context=context):
            result[line.distinta_id.id] = True
        return result.keys()

    def _get_amount_total(self, cr, uid, ids, field_name, arg, context=None):
        r = {}
        for id in ids:
            tot = 0.0
            distinta = self.browse(cr, uid, id, context=context)
            for line in distinta.line_ids: 
                tot += line.amount              
            r[id] = tot
        return r

    _name = 'riba.distinta'
    _description = 'Distinta Riba'

    _columns = {
        'name': fields.char('Reference', size=128, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'config': fields.many2one('riba.configurazione', 'Configuration', 
            select=True, required=True, readonly=True, states={'draft': [('readonly', False)]}, 
            help='Riba configuration to be used'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('accepted', 'Accepted'),
            ('accredited', 'Accredited'),
            ('paid', 'Paid'),
            ('unsolved', 'Unsolved'),
            ('cancel', 'Canceled')], 'State', select=True, readonly=True),
        'line_ids': fields.one2many('riba.distinta.line', 'distinta_id',
            'Riba deadlines', readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', 'User', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date_created': fields.date('Creation date', readonly=True),
        'date_accepted': fields.date('Acceptance date', readonly=True),
        'date_accreditation': fields.date('Accreditation date', readonly=True),
        'date_paid': fields.date('Paid date', readonly=True),
        'date_unsolved': fields.date('Unsolved date', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'acceptance_move_ids': fields.function(_get_acceptance_move_ids, type='many2many', relation='account.move', method=True, string="Acceptance Entries"),
        'accreditation_move_id': fields.many2one('account.move', 'Accreditation Entry', readonly=True),
        'payment_ids': fields.function(_get_payment_ids, relation='account.move.line', type="many2many", string='Payments'),
        'unsolved_move_ids': fields.function(_get_unsolved_move_ids, type='many2many', relation='account.move', method=True, string="Unsolved Entries"),
        'type': fields.related('config', 'tipo', type='char', size=32, string='Type', readonly=True),
        'registration_date': fields.date(
            'Registration Date',
            states={'draft': [('readonly', False)],
                    'cancel': [('readonly', False)], },
            select=True,
            readonly=True,
            required=True,
            help="Keep empty to use the current date"),
        'amount_total': fields.function(_get_amount_total, copy=False, type="float", digits_compute=dp.get_precision('Account'), string='Totale',
            store=False),                  
    }

    _defaults = {
        'user_id': lambda self,cr,uid,context: uid,
        'date_created': fields.date.context_today,
        'name': lambda self,cr,uid,context: self.pool.get('ir.sequence').get(cr, uid, 'riba.distinta'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'riba.distinta', context=c),
        'registration_date': fields.date.context_today,
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for distinta in self.browse(cr, uid, ids, context=context):
            if distinta.state not in ('draft',  'cancel'):
                raise orm.except_orm(_('Error'),_('Distinta %s is in state %s. You can only delete documents in state draft or canceled') % (distinta.name, distinta.state))
        super(riba_distinta,self).unlink(cr, uid, ids, context=context)
        return True

    def confirm(self, cr, uid, ids, context=None):
        line_pool = self.pool.get('riba.distinta.line')
        
        if context is None: context = {}

        for distinta in self.browse(cr, uid, ids, context=context):
            # INIZIO REPERIMENTO PERIODO FISCALE
            dt = distinta.registration_date
            args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
            
            if distinta.company_id:
                company = distinta.company_id.id
            else:
                company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
                
            args.append(('company_id', '=', company))        
            period_id = self.pool.get('account.period').search(cr, uid, args, context=context)
            if period_id:
                context.update({'period_id':period_id[0]})
            else:
                context.update({'period_id':False})                
            #FINE REPERIMENTO PERIODO FISCALE                         
            line_pool.confirm(cr, uid, [line.id for line in distinta.line_ids], context=context)
        return True
    
    def riba_new(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'draft',
            }, context=context)
        return True
    
    def riba_cancel(self, cr, uid, ids, context=None):
        for distinta in self.browse(cr, uid, ids, context=context):
            # TODO remove every other move
            for line in distinta.line_ids:
                if line.acceptance_move_id:
                    line.acceptance_move_id.unlink()
                if line.unsolved_move_id:
                    line.unsolved_move_id.unlink()
            if distinta.accreditation_move_id:
                distinta.accreditation_move_id.unlink()
        self.write(cr, uid, ids, {
            'state': 'cancel',
            }, context=context)
        return True
    
    def riba_accepted(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'accepted',
            'date_accepted': fields.date.context_today(
                self, cr, uid, context),
            }, context=context)
        return True
    
    def riba_accredited(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'accredited',
            'date_accreditation': fields.date.context_today(
                self, cr, uid, context),
            }, context=context)
        for distinta in self.browse(cr, uid, ids, context=context):
            for line in distinta.line_ids:
                line.write({'state': 'accredited'})
        return True
    
    def riba_paid(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'paid',
            'date_paid': fields.date.context_today(
                self, cr, uid, context),
            }, context=context)
        return True
    
    def riba_unsolved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'unsolved',
            'date_unsolved': fields.date.context_today(
                self, cr, uid, context),
            }, context=context)
        return True
        
    def test_accepted(self, cr, uid, ids, context):
        for distinta in self.browse(cr, uid, ids):
            for line in distinta.line_ids:
                if line.state != 'confirmed':
                    return False
        return True
        
    def test_unsolved(self, cr, uid, ids, context):
        for distinta in self.browse(cr, uid, ids):
            for line in distinta.line_ids:
                if line.state != 'unsolved':
                    return False
        return True
        
    def test_paid(self, cr, uid, ids, context):
        for distinta in self.browse(cr, uid, ids):
            for line in distinta.line_ids:
                if line.state != 'paid':
                    return False
        return True
        
    def action_cancel_draft(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state':'draft'})

        for distinta_id in ids:
            workflow.trg_delete(uid, 'riba.distinta', distinta_id, cr)
            workflow.trg_create(uid, 'riba.distinta', distinta_id, cr)
        return True
