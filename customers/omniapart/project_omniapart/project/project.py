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

from openerp.osv import fields, orm, osv
from openerp import api
from openerp.tools.translate import _

class project_task_type_omniapart(orm.Model):
    _inherit = "project.task.type"
    
    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
        for task_type in self.browse(cr, uid, ids, context=context):
            if task_type.project_ids:
                raise osv.except_osv(_('User Error!'), _('You cannot delete a stage linked to a project.'))
            if self.pool.get('project.task').search(cr, uid, [('stage_id','=',task_type.id)]):
                raise osv.except_osv(_('User Error!'), _('You cannot delete a stage linked to a task.'))   
            if self.pool.get('project.task.history').search(cr, uid, [('type_id','=',task_type.id)]):
                raise osv.except_osv(_('User Error!'), _('You cannot delete a stage that was used in a task.'))                            
        return super(project_task_type_omniapart, self).unlink(cr, uid, ids, context=context)

class project_omniapart(orm.Model):
    _inherit = "project.project"

    _columns = {
        'standard_id': fields.many2one('accreditation.standard',
                                       'Norma'),
        'check': fields.selection([('none', 'Nessuno'),
                                  ('z', 'Solo Zona'),
                                  ('s', 'Solo Norma'),
                                  ('sz', 'Norma e Zona'),
                                  ('se', 'Norma ed EA'),
                                  ('sez', 'Norma, EA e Zona'),
                                  ('sen', 'Norma, EA e NACE'),
                                  ('senz', 'Tutto')],
                                  'Controlli da effettuare'),
        }

    _defaults = {
        'check': 'none',
    }

    def onchange_standard_id(self, cr, uid, ids, standard_id, context=None):
        if not standard_id:
            return {}
        res = {}

        cr.execute('SELECT prtn.id FROM res_partner AS prtn WHERE is_partner_level2 = TRUE AND prtn.internal_standard_ids LIKE %s',('%,'+str(standard_id)+',%',))
        domain = cr.fetchall()
        res['domain'] = ({'prospect_id': [('id', 'in', domain)]})
        return res

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                     subtype=None, parent_id=False, attachments=None, context=None, **kwargs):

        if context is None:
            context = {}
            
        if 'default_model' in context and 'mail_post_autofollow' in context and context['default_model'] == 'project.project':
            context['mail_post_autofollow'] = False

        return super(project_omniapart,self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, **kwargs)
