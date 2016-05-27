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
from openerp import SUPERUSER_ID

class wizard_message_attach(osv.osv_memory):
    _name = "wizard.message.attach"
    _description = "Message Attach"       

    _columns = {
        'message_id': fields.many2one('mail.message', string='Message'),
        'model_id': fields.many2one('ir.model', string='Model'),
        'res_id': fields.integer(string='Object'),
        'search_string': fields.char(string='Search'),
        'line_ids': fields.one2many('wizard.message.attach.line','wizard_id','Oggetti disponibili'),
    }

    def _get_msg_id(self, cr, uid, context=None):
        if 'message_id' in context and context['message_id']:
            return context['message_id']
        return False

    def _get_model_id(self, cr, uid, context=None):
        if 'message_id' in context and context['message_id']:
            t_model = self.pool.get('mail.message').browse(cr, uid, context['message_id']).model
            if t_model:
                model = self.pool.get('ir.model').search(cr, uid, [('model','=',t_model)])
                if model and model[0]:
                    return model[0]
        return False

    def _get_res_id(self, cr, uid, context=None):
        if 'message_id' in context and context['message_id']:
            return self.pool.get('mail.message').browse(cr, uid, context['message_id']).res_id
        return False

    _defaults = {
                 'message_id': _get_msg_id,
                 'model_id': _get_model_id,
                 'res_id': _get_res_id,
     }
    
    def attach_message(self, cr, uid, ids, context=None):
        wiz_obj = self.browse(cr,uid,ids[0])
        msg_id = wiz_obj.message_id.id
        model = wiz_obj.model_id.model
        res_id = wiz_obj.res_id
        self.pool.get('mail.message').write(cr,SUPERUSER_ID,msg_id,{'model': model, 'res_id': res_id})
        return

    def onchange_model_id(self, cr, uid, ids, model_id, context=None):
        if context is None:
            context = {}
        model = self.pool.get('ir.model').browse(cr,uid,model_id)
        if model:
            res = []
            obj_obj = self.pool.get(model.model)
            obj_ids = obj_obj.search(cr, uid, [('id','>',0)], limit=400)
            for id in obj_ids:
                res.append((0,0,{'res_id':id, 'object_name': obj_obj.browse(cr,uid,id).name}))              

            return {'value': {'line_ids':res, 'search_string':''}}
        else:
            return {'value':{'line_ids': {}, 'search_string':''}}

    def onchange_search_string(self, cr, uid, ids, model_id, search_string , context=None):
        if context is None:
            context = {}
        model = self.pool.get('ir.model').browse(cr,uid,model_id)
        if model:
            res = []
            obj_obj = self.pool.get(model.model)
            if search_string:
                obj_ids = obj_obj.search(cr, uid, [('id','>',0),('name','ilike',search_string)], limit=400)
            else:
                obj_ids = obj_obj.search(cr, uid, [('id','>',0)], limit=400)                
            for id in obj_ids:
                res.append((0,0,{'res_id':id, 'object_name': obj_obj.browse(cr,uid,id).name}))              

            return {'value': {'line_ids':res}}
        else:
            return {}

class wizard_message_attach_line(osv.osv_memory):
    _name = "wizard.message.attach.line"
    _description = "Message Attach Line"

    _columns = {
        'res_id': fields.integer(string='ID'),
        'object_name': fields.char(string='Name'),
        'wizard_id': fields.many2one('wizard.message.attach.line','wizard_id','Wizard ID'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    