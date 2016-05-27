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

class wizard_message_attach_omniapart(osv.osv_memory):
    _inherit = "wizard.message.attach"

    @api.model
    def _get_domain(self):
        res = self.pool.get('ir.model').search(self._cr, self._uid, [('model','in',['project.project','project.task','account.analytic.account'])])
        domain=[('id','in', res)]
        return domain

    _columns = {
        'model_id': fields.many2one('ir.model', string='Model', domain=_get_domain),
    }

    def _get_model_id(self, cr, uid, context=None):
        if 'message_id' in context and context['message_id']:
            t_model = self.pool.get('mail.message').browse(cr, uid, context['message_id']).model
            if t_model and t_model in ['project.project','project.task','account.analytic.account']:
                model = self.pool.get('ir.model').search(cr, uid, [('model','=',t_model)])
                if model and model[0]:
                    return model[0]
        return False

    def _get_res_id(self, cr, uid, context=None):
        if 'message_id' in context and context['message_id']:
            if self.pool.get('mail.message').browse(cr, uid, context['message_id']).model in ['project.project','project.task','account.analytic.account']:
                return self.pool.get('mail.message').browse(cr, uid, context['message_id']).res_id
        return False

    _defaults = {
                 'model_id': _get_model_id,
                 'res_id': _get_res_id,
     }

    def onchange_model_id(self, cr, uid, ids, model_id, context=None):
        if context is None:
            context = {}
        model = self.pool.get('ir.model').browse(cr,uid,model_id)            
        if model:
            if model.model != 'project.task':
                return super(wizard_message_attach_omniapart, self).onchange_model_id(cr, uid, ids, model_id, context=context)
            else:            
                res = []
                task_obj = self.pool.get('project.task')
                task_ids = task_obj.search(cr, uid, [('id','>',0)], limit=400)
                for id in task_ids:
                    t_name = ''
                    task_data = task_obj.browse(cr, uid, id)
                    if task_data.project_id:
                        t_name += task_data.project_id.name + ' - '
                    t_name += task_data.name
                    res.append((0,0,{'res_id':id, 'object_name': t_name }))              

                return {'value': {'line_ids':res, 'search_string':''}}
        else:
            return {'value':{'line_ids': {}, 'search_string':''}}

    def onchange_search_string(self, cr, uid, ids, model_id, search_string , context=None):
        if context is None:
            context = {}
        model = self.pool.get('ir.model').browse(cr,uid,model_id)
        if model:
            if model.model != 'project.task':
                return super(wizard_message_attach_omniapart, self).onchange_search_string(cr, uid, ids, model_id, search_string, context=context)
            else:
                res = []
                task_obj = self.pool.get('project.task')
                if search_string:
                    project_obj = self.pool.get('project.project')                    
                    project_ids = project_obj.search(cr, uid, [('id','>',0),('name','ilike',search_string)], limit=400)                    
                    task_ids = task_obj.search(cr, uid, [('id','>',0),'|',('name','ilike',search_string),('project_id','in',project_ids)], limit=400)
                else:
                    task_ids = task_obj.search(cr, uid, [('id','>',0)], limit=400)                
                for id in task_ids:
                    t_name = ''
                    task_data = task_obj.browse(cr, uid, id)
                    if task_data.project_id:
                        t_name += task_data.project_id.name + ' - '
                    t_name += task_data.name                    
                    res.append((0,0,{'res_id':id, 'object_name': t_name }))              
    
                return {'value': {'line_ids':res}}
        else:
            return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    