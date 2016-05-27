# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#    Copyright (C) Francesco Apruzzese
#    Copyright (C) 2014 Agile Business Group (http://www.agilebg.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import fields
from openerp import models
from openerp import api
from openerp import _
from openerp.exceptions import Warning


class wizard_duplicate_other_type(models.TransientModel):

    _name = "wizard.duplicate.other.type"

    document_type_id = fields.Many2one('sale.document.type',string="Document Type")

    def do_copy(self, cr, uid, ids, context=None):
        wiz = self.browse(cr,uid,ids,context=context)[0]
        new_ids = []
        if 'active_ids' in context and context['active_ids']:
            for id in context['active_ids']:
                if wiz.document_type_id:
                    document_type_id = wiz.document_type_id.id
                else:
                    document_type_id = None
                origin = self.pool.get('sale.order').browse(cr,uid,id,context=context).name
                new_id = self.pool.get('sale.order').copy(cr, uid, id, {'document_type_id':document_type_id, 'origin':origin}, context=context)
                new_ids.append(new_id)   
        else: 
            raise Warning(_("You have to select at least a document to duplicate"))     

        if new_ids:
            if len(new_ids) == 1:        
                mod_obj = self.pool.get('ir.model.data')
                result = mod_obj.get_object_reference(cr, uid,
                                                      'sale',
                                                      'view_order_form')
                view_id = result and result[1] or False
        
                return {
                        'view_type': 'form',
                        'view_mode': 'form,tree',
                        'res_model': 'sale.order',
                        'type': 'ir.actions.act_window',
                        'context': context,
                        'res_id': new_id,
                        'views': [(view_id,'form'),(False,'tree')],
                        }        
            else:
                mod_obj = self.pool.get('ir.model.data')
                result = mod_obj.get_object_reference(cr, uid,
                                                      'sale',
                                                      'view_quotation_tree')
                                        
                view_id = result and result[1] or False
        
                return {'domain': "[('id','in', ["+','.join(map(str,new_ids))+"])]",
                        'name': _("Nuovi Ordini:"),
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'sale.order',
                        'type': 'ir.actions.act_window',
                        'context': context,
                        'views': [(False,'tree'),(view_id,'form')],
                        }               
        else:
            return