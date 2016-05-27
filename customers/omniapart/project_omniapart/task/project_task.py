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

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import api

class project_task(orm.Model):
    _inherit = "project.task"

    _columns = {
                'meeting_id':  fields.many2one('calendar.event', 'Meeting'),  
                'insert_in_calendar': fields.boolean('Inserisci in calendario azienda'),  
                'force_overlaying': fields.boolean('Forza Sovrapposizione'),            
                'project_id': fields.many2one('project.project', 'Project', ondelete='set null', select=True, track_visibility='always', change_default=True),                
                'prospect_id': fields.related('project_id', 'prospect_id', type='many2one', relation="res.partner", string="Prospect", domain=[('is_partner_level2', '=', True)],),
                'zig': fields.related('project_id', 'zig', type='char', string="ZIG"),
                'c_number': fields.related('project_id', 'c_number', type='char', string='N.Contratto'),
                'start_hour': fields.char('Ora di Inizio'), 
                'end_hour': fields.char('Ora di Fine'),           
                'referent_name': fields.char('Referente Aziendale'),
                'lavoration_notes': fields.text('Note Intervento'),                                     
                'check': fields.selection([('none', 'Nessuno'),
                                          ('z', 'Solo Zona'),
                                          ('s', 'Solo Norma'),
                                          ('sz', 'Norma e Zona'),
                                          ('se', 'Norma ed EA'),
                                          ('sez', 'Norma, EA e Zona'),
                                          ('sen', 'Norma, EA e NACE'),
                                          ('senz', 'Tutto')],
                                          string='Controlli da effettuare'),
                }

    def _get_check_default(self, cr, uid, context=None):
        proj_obj = self.pool['project.project']
        if 'active_id' in context:
            return proj_obj.browse(cr, uid, context['active_id']).check
        else:
            return 'none'

    _defaults = {
        'check': _get_check_default,
        'insert_in_calendar': False,
        'force_overlaying': False,
    }

    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                     subtype=None, parent_id=False, attachments=None, context=None, **kwargs):

        if context is None:
            context = {}
            
        ctx = {}
        for item in context.items():
            ctx[item[0]] = item[1]       
            
        if 'default_model' in ctx and 'mail_post_autofollow' in ctx and ctx['default_model'] == 'project.task':
            ctx['mail_post_autofollow'] = False

        return super(project_task,self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=ctx, **kwargs)


    def onchange_project(self, cr, uid, ids, project_id, context=None):
        if project_id:
            res = super(project_task, self).onchange_project(cr, uid, ids, project_id)
            project = self.pool.get('project.project').browse(cr, uid, project_id, context=context)
            res['value'].update({'check': project.check})
            if project and project.prospect_id:
                res['value'].update({'prospect_id': project.prospect_id.id, })
                return res
        return {}

    def _onchange_check_internal(self, cr, sql):
        cr.execute(sql)
        return set(cr.fetchall())

    def _onchange_check_ea(self, cr, uid, domain, ea_id_in, std_id):
        sql_ea = 'SELECT DISTINCT usrs.id FROM res_users AS usrs, res_partner AS prtn, standard_sector_link AS link, accreditation_sector_ea_standard_sector_link_rel AS rel, res_partner_category_standard_sector_link_rel AS pl_rel WHERE rel.standard_sector_link_id = link.id AND link.partner_id = prtn.id AND usrs.partner_id = prtn.id AND rel.accreditation_sector_ea_id = '
        link_obj = self.pool.get('standard.sector.link')

        link_ids = link_obj.search(cr, uid, [('id', 'in', ea_id_in), ('standard_id', '=', std_id)])
        if link_ids:
            ea_ids = link_obj.browse(cr, uid, link_ids[0]).ea_sector_ids.ids
            for ea_id in ea_ids:
                cr.execute(sql_ea + str(ea_id))
                domain = domain & set(cr.fetchall())
                if not domain:
                    break
        return domain

    def _onchange_check_nace(self, cr, uid, domain, nace_id_in, std_id):
        sql_nace = 'SELECT DISTINCT usrs.id FROM res_users AS usrs, res_partner AS prtn, standard_sector_link AS link, res_partner_category_standard_sector_link_rel AS rel, res_partner_category_standard_sector_link_rel AS pl_rel WHERE rel.standard_sector_link_id = link.id AND link.partner_id = prtn.id AND usrs.partner_id = prtn.id AND rel.res_partner_category_id = '
        link_obj = self.pool.get('standard.sector.link')

        link_ids = link_obj.search(cr, uid, [('id', 'in', nace_id_in), ('standard_id', '=', std_id)])
        if link_ids:
            nace_ids = link_obj.browse(cr, uid, link_ids[0]).nace_sector_ids.ids
            for nace_id in nace_ids:
                cr.execute(sql_nace + str(nace_id))
                domain = domain & set(cr.fetchall())
                if not domain:
                    break
        return domain

    def onchange_checks(self, cr, uid, ids, project, check, context=None):
        if not project:
            return {}

        project_obj = self.pool.get('project.project')

        project_data = project_obj.browse(cr, uid, project)
        prospect_data = project_data.prospect_id

        sql_zone = 'SELECT usrs.id FROM res_users AS usrs, res_partner AS prtn, hr_employee AS empl, hr_employee_res_region_rel AS rel, resource_resource AS res WHERE rel.hr_employee_id = empl.id AND empl.resource_id = res.id AND res.user_id = usrs.id AND usrs.partner_id = prtn.id AND rel.res_region_id = ' + str(prospect_data.region.id)        
        sql_standard = 'SELECT usrs.id FROM res_users AS usrs, res_partner AS prtn, standard_sector_link AS link WHERE link.standard_id = '+str(project_data.standard_id.id)+' AND link.partner_id = usrs.partner_id AND usrs.partner_id = prtn.id'  
        sql_none = 'SELECT usrs.id FROM res_users AS usrs'

        res = {}
        domain = set()

        if check == 'none':
            domain = self._onchange_check_internal(cr, sql_none)

        elif check == 'z':
            if prospect_data and prospect_data.region:
                domain = self._onchange_check_internal(cr, sql_zone)
            else:
                return {}

        elif check == 's':
            if project_data.standard_id:
                domain = self._onchange_check_internal(cr, sql_standard)
            else:
                return {}

        elif check == 'sz':
            if prospect_data and prospect_data.region and project_data.standard_id:
                domain = self._onchange_check_internal(cr, sql_standard + ' INTERSECT ' + sql_zone)
            else:
                return {}

        elif check == 'se':
            if project_data.standard_id:
                domain = self._onchange_check_internal(cr, sql_standard)
                domain = self._onchange_check_ea(cr, uid, domain, prospect_data.standard_ea_rel_ids.ids, project_data.standard_id.id)
            else:
                return {}

        elif check == 'sez':
            if prospect_data and prospect_data.region and project_data.standard_id:
                domain = self._onchange_check_internal(cr, sql_standard + ' INTERSECT ' + sql_zone)
                domain = self._onchange_check_ea(cr, uid, domain, prospect_data.standard_ea_rel_ids.ids, project_data.standard_id.id)
            else:
                return {}

        elif check == 'sen':
            if project_data.standard_id:
                domain = self._onchange_check_internal(cr, sql_standard)
                domain = self._onchange_check_ea(cr, uid, domain, prospect_data.standard_ea_rel_ids.ids, project_data.standard_id.id)
                domain = self._onchange_check_nace(cr, uid, domain, prospect_data.standard_ea_rel_ids.ids, project_data.standard_id.id) 
            else:
                return {}

        elif check == 'senz':
            if prospect_data and prospect_data.region and project_data.standard_id:
                domain = self._onchange_check_internal(cr, sql_standard + ' INTERSECT ' + sql_zone)
                domain = self._onchange_check_ea(cr, uid, domain, prospect_data.standard_ea_rel_ids.ids, project_data.standard_id.id)
                domain = self._onchange_check_nace(cr, uid, domain, prospect_data.standard_ea_rel_ids.ids, project_data.standard_id.id)
            else:
                return {}

        domain = list(domain)
        res['domain'] = ({'user_id': [('id', 'in', domain)]})
        res['value'] = ({'user_id': None})
        return res

    def do_close(self, cr, uid, ids, context=None): 
        """ Closes Task """
        if not isinstance(ids, list):
            ids = [ids]
        for task in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [task.id], {'color': 4, 'kanban_state':'done'}, context=context)
            cr.execute('''
                UPDATE project_task
                SET progress = %s
                WHERE id = %s
            ''',(100.0, task.id))
            None
        return True

    def create(self, cr, uid, vals, context=None):

        if 'user_id' not in vals or not vals['user_id'] or 'date_start' not in vals or not vals['date_start'] or 'date_end' not in vals or not vals['date_end']:
            task_res = super(project_task, self).create(cr, uid, vals, context=context)
            return task_res

        user_obj = self.pool.get('res.users')
        meeting_obj = self.pool.get('calendar.event')
        task_obj = self.pool.get('project.task')
        user_data = user_obj.browse(cr, uid, vals['user_id'])

        t_date_start = None
        t_date_end = None
        t_name = ''
        t_description = ''
        t_force_overlaying = False
        t_insert_in_calendar = False

        if 'force_overlaying' in vals and vals['force_overlaying']:
            t_force_overlaying = vals['force_overlaying']
        if 'insert_in_calendar' in vals and vals['insert_in_calendar']:
            t_insert_in_calendar = vals['insert_in_calendar']            
        if 'date_start' in vals and vals['date_start']:
            t_date_start = vals['date_start']
        if 'date_end' in vals and vals['date_end']:
            t_date_end = vals['date_end']
        if 'description' in vals and vals['description']:
            t_description = vals['description']
        if 'name' in vals and vals['name']:
            t_name = vals['name']            
        
        if not t_force_overlaying and t_insert_in_calendar:            
            meeting_ids = meeting_obj.search(cr, uid,
                                             [('partner_ids', '=', user_data.partner_id.id),
                                              ('show_as', '=', 'busy'),
                                              '|', '&', ('start_datetime', '<=', t_date_end),
                                                        ('start_datetime', '>=', t_date_start),
                                              '|', '&', ('stop_datetime', '>=', t_date_start),
                                                        ('stop_datetime', '<=', t_date_end),
                                                   '&', ('start_datetime', '<=', t_date_start),
                                                        ('stop_datetime', '>=', t_date_end),
                                              ])
            activity_ids = task_obj.search(cr, uid, 
                                              [('insert_in_calendar','=', True),
                                              '|', '&', ('date_start', '<=', t_date_end),
                                                        ('date_start', '>=', t_date_start),
                                              '|', '&', ('date_end', '>=', t_date_start),
                                                        ('date_end', '<=', t_date_end),
                                                   '&', ('date_start', '<=', t_date_start),
                                                        ('date_end', '>=', t_date_end),
                                              ])
            if meeting_ids or activity_ids:
                raise orm.except_orm(_('Error'),
                                     _("La persona è già impegnata nella data specificata!"))

        meeting_vals = {
            'name': t_name,
            'description': t_description,
            'user_id': user_data.id,
            'allday': False,
            'state': 'open',
            'class': 'public',
            'partner_ids': [(4, user_data.partner_id.id)],
            'show_as': 'busy',
            'start_datetime': t_date_start,
            'stop_datetime': t_date_end,
        }
    
        context.update({'update_meeting':True})
        
        if 'insert_in_calendar' in vals and vals['insert_in_calendar']:
            meeting_res = meeting_obj.create(cr, uid, meeting_vals, context=context)           
            vals.update({'meeting_id':meeting_res})
        
        task_res = super(project_task, self).create(cr, uid, vals, context=context)

        if 'insert_in_calendar' in vals and vals['insert_in_calendar']:        
            meeting_obj.write(cr,uid,meeting_res,{'task_id':task_res}, context=context)

        return task_res

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        user_obj = self.pool.get('res.users')
        meeting_obj = self.pool.get('calendar.event')
        task_obj = self.pool.get('project.task')
        result = None

        for task in self.browse(cr, uid, ids, context=context):
            t_meeting_id = task.meeting_id and task.meeting_id.id or 0            
            t_user_id = task.user_id and task.user_id.id or None
            t_date_start = task.date_start
            t_date_end = task.date_end
            t_description = task.description
            t_name = task.name
            t_force_overlaying = task.force_overlaying
            t_insert_in_calendar = task.insert_in_calendar

            if 'force_overlaying' in vals:
                t_force_overlaying = vals['force_overlaying']
            if 'insert_in_calendar' in vals:
                t_insert_in_calendar = vals['insert_in_calendar']                
            if 'user_id' in vals and vals['user_id']:
                t_user_id = vals['user_id']
            if 'date_start' in vals and vals['date_start']:
                t_date_start = vals['date_start']
            if 'date_end' in vals and vals['date_end']:
                t_date_end = vals['date_end']
            if 'description' in vals and vals['description']:
                t_description = vals['description']
            if 'name' in vals and vals['name']:
                t_name = vals['name']

            user_data = user_obj.browse(cr, uid, t_user_id)

            if not t_user_id or not t_date_start or not t_date_end:
                result = super(project_task, self).write(cr,
                                                         uid,
                                                         [task.id],
                                                         vals,
                                                         context=context)
                continue

            if not t_force_overlaying and t_insert_in_calendar:            
                meeting_ids = meeting_obj.search(cr, uid,
                                                 [('partner_ids', '=', user_data.partner_id.id),
                                                  ('show_as', '=', 'busy'),
                                                  ('id', '!=', t_meeting_id),
                                                  ('task_id', '!=', ids[0]),
                                                  '|', '&', ('start_datetime', '<=', t_date_end),
                                                            ('start_datetime', '>=', t_date_start),
                                                  '|', '&', ('stop_datetime', '>=', t_date_start),
                                                            ('stop_datetime', '<=', t_date_end),
                                                       '&', ('start_datetime', '<=', t_date_start),
                                                            ('stop_datetime', '>=', t_date_end),
                                                  ])
    
                activity_ids = task_obj.search(cr, uid, 
                                                  [('user_id', '=', t_user_id),
                                                   ('insert_in_calendar','=', True),
                                                   ('id', '!=', task.id),
                                                  '|', '&', ('date_start', '<=', t_date_end),
                                                            ('date_start', '>=', t_date_start),
                                                  '|', '&', ('date_end', '>=', t_date_start),
                                                            ('date_end', '<=', t_date_end),
                                                       '&', ('date_start', '<=', t_date_start),
                                                            ('date_end', '>=', t_date_end),
                                                  ])
    
                if meeting_ids or activity_ids:
                    raise orm.except_orm(_('Error'),
                                         _("La persona è già impegnata nella data specificata!"))

            meeting_vals = {
                'name': t_name,
                'description': t_description,
                'user_id': user_data.id,
                'allday': False,
                'state': 'open',
                'class': 'public',
                'partner_ids': [(4, user_data.partner_id.id)],
                'show_as': 'busy',
                'start_datetime': t_date_start,
                'stop_datetime': t_date_end,
                'task_id': task.id,
            }

            
            if 'insert_in_calendar' in vals and vals['insert_in_calendar']:            
                context.update({'update_meeting':True})
                if not t_meeting_id:
                    t_meeting_id = meeting_obj.create(cr, uid, meeting_vals, context=context)
                    vals.update({'meeting_id':t_meeting_id})                
                meeting_obj.write(cr, uid, t_meeting_id, meeting_vals, context=context)
            elif 'insert_in_calendar' in vals and not vals['insert_in_calendar']:
                if t_meeting_id:
                    context.update({'delete_meeting':True})                    
                    meeting_obj.unlink(cr, uid, t_meeting_id, context)
                    vals.update({'meeting_id':None})
            else:
                if t_meeting_id:
                    context.update({'update_meeting':True})                    
                    meeting_obj.write(cr, uid, t_meeting_id, meeting_vals, context=context)                    
             
                           
            result = super(project_task, self).write(cr, uid, [task.id], vals, context=context)
        return result

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        context.update({'delete_meeting':True})
        for id in self.browse(cr,uid,ids):
            if id.meeting_id:
                self.pool.get('calendar.event').unlink(cr, uid, id.meeting_id.id, context)

        res = super(project_task, self).unlink(cr, uid, ids, context)
        return res
