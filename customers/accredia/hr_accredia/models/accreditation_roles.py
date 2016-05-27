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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class accreditation_roles(orm.Model):

    _name = "accreditation.roles"
    _description = "Ruoli"

    def _get_empty_dict(self):

        return {'value': {'technical_officer': None,
                          'supervisor': None,
                          'inspector': None,
                          'inspector_system': None,
                          'relator': None,
                          'correlator': None,
                          'evaluator': None,
                          'direction_repr': None,
                          'observer': None,
                          'technical_expert': None,
                          'resp_group_inspection': None,
                          'assistant_inspection': None,
                          'department_director': None,
                          'secretary_management': None,
                          'candidate': None,
                          }
                }

    def onchange_technical_officer(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['technical_officer']
        return res

    def onchange_supervisor(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['supervisor']
        return res

    def onchange_inspector(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['inspector']
        return res

    def onchange_inspector_system(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['inspector_system']
        return res

    def onchange_relator(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['relator']
        return res

    def onchange_correlator(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['correlator']
        return res

    def onchange_evaluator(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['evaluator']
        return res

    def onchange_direction_repr(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['direction_repr']
        return res

    def onchange_observer(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['observer']
        return res

    def onchange_technical_expert(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['technical_expert']
        return res

    def onchange_resp_group_inspection(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['resp_group_inspection']
        return res

    def onchange_assistant_inspection(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['assistant_inspection']
        return res

    def onchange_department_director(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['department_director']
        return res

    def onchange_secretary_management(self, cr, uid, ids, data, context=None):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['secretary_management']
        return res

    def onchange_candidate(self, cr, uid, ids, data):
        if not data:
            return {}
        res = self._get_empty_dict()
        del res['value']['candidate']
        return res

    _rec_name = "description"

    _columns = {
        'description': fields.text('Description', required=True),
        'billable': fields.boolean('Billable'),

        'technical_officer': fields.boolean('Technical Officer'),
        'supervisor': fields.boolean('Supervisor'),
        'inspector': fields.boolean('Ispettore Tecnico'),

        'inspector_system': fields.boolean('Ispettore di sistema'),
        'relator': fields.boolean('Relatore'),
        'correlator': fields.boolean('Correlatore'),
        'evaluator': fields.boolean('Evaluator'),
        'direction_repr': fields.boolean('Rappresentante della direzione'),
        'observer': fields.boolean('Osservatore'),
        'technical_expert': fields.boolean('Esperto tecnico'),
        'resp_group_inspection': fields.boolean('Responsabile Gruppo Verifica Ispettiva'),
        'assistant_inspection': fields.boolean('Assistente Verifica Ispettiva'),
        'department_director': fields.boolean('Direttore Di Dipartimento'),
        'secretary_management': fields.boolean('Segreteria/Amministrazione'),
        'candidate': fields.boolean('Candidato'),

        }

    def create(self, cr, user, vals, context=None):
        # ad eccezione del campo "FATTURABILE" può essere scelto un solo ruolo.
        t_count = 0

        if 'technical_officer' in vals and vals['technical_officer']:
            t_count = t_count + 1

        if 'supervisor' in vals and vals['supervisor']:
            t_count = t_count + 1

        if 'inspector' in vals and vals['inspector']:
            t_count = t_count + 1

        if 'inspector_system' in vals and vals['inspector_system']:
            t_count = t_count + 1

        if 'relator' in vals and vals['relator']:
            t_count = t_count + 1

        if 'correlator' in vals and vals['correlator']:
            t_count = t_count + 1

        if 'evaluator' in vals and vals['evaluator']:
            t_count = t_count + 1

        if 'direction_repr' in vals and vals['direction_repr']:
            t_count = t_count + 1

        if 'observer' in vals and vals['observer']:
            t_count = t_count + 1

        if 'technical_expert' in vals and vals['technical_expert']:
            t_count = t_count + 1

        if 'resp_group_inspection' in vals and vals['resp_group_inspection']:
            t_count = t_count + 1

        if 'assistant_inspection' in vals and vals['assistant_inspection']:
            t_count = t_count + 1

        if 'department_director' in vals and vals['department_director']:
            t_count = t_count + 1

        if 'secretary_management' in vals and vals['secretary_management']:
            t_count = t_count + 1

        if 'candidate' in vals and vals['candidate']:
            t_count = t_count + 1

        if t_count > 1:
            raise orm.except_orm(_('Errore'),
                                 _("Non è possibile impostare più di un ruolo!"))

        res = super(accreditation_roles, self).create(cr, user, vals, context)

        return res

    def write(self, cr, uid, ids, vals, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        for data in self.browse(cr, uid, ids):
            # ad eccezione del campo "FATTURABILE" può essere scelto un solo ruolo.

            t_count = 0

            if 'technical_officer' in vals and vals['technical_officer']:
                t_count = t_count + 1
            elif 'technical_officer' not in vals:
                if data.technical_officer:
                    t_count = t_count + 1

            if 'supervisor' in vals and vals['supervisor']:
                t_count = t_count + 1
            elif 'supervisor' not in vals:
                if data.supervisor:
                    t_count = t_count + 1

            if 'inspector' in vals and vals['inspector']:
                t_count = t_count + 1
            elif 'inspector' not in vals:
                if data.inspector:
                    t_count = t_count + 1

            if 'inspector_system' in vals and vals['inspector_system']:
                t_count = t_count + 1
            elif 'inspector_system' not in vals:
                if data.inspector_system:
                    t_count = t_count + 1

            if 'relator' in vals and vals['relator']:
                t_count = t_count + 1
            elif 'relator' not in vals:
                if data.relator:
                    t_count = t_count + 1

            if 'correlator' in vals and vals['correlator']:
                t_count = t_count + 1
            elif 'correlator' not in vals:
                if data.correlator:
                    t_count = t_count + 1

            if 'evaluator' in vals and vals['evaluator']:
                t_count = t_count + 1
            elif 'evaluator' not in vals:
                if data.evaluator:
                    t_count = t_count + 1

            if 'direction_repr' in vals and vals['direction_repr']:
                t_count = t_count + 1
            elif 'direction_repr' not in vals:
                if data.direction_repr:
                    t_count = t_count + 1

            if 'observer' in vals and vals['observer']:
                t_count = t_count + 1
            elif 'observer' not in vals:
                if data.observer:
                    t_count = t_count + 1

            if 'technical_expert' in vals and vals['technical_expert']:
                t_count = t_count + 1
            elif 'technical_expert' not in vals:
                if data.technical_expert:
                    t_count = t_count + 1

            if 'resp_group_inspection' in vals and vals['resp_group_inspection']:
                t_count = t_count + 1
            elif 'resp_group_inspection' not in vals:
                if data.resp_group_inspection:
                    t_count = t_count + 1

            if 'assistant_inspection' in vals and vals['assistant_inspection']:
                t_count = t_count + 1
            elif 'assistant_inspection' not in vals:
                if data.assistant_inspection:
                    t_count = t_count + 1

            if 'department_director' in vals and vals['department_director']:
                t_count = t_count + 1
            elif 'department_director' not in vals:
                if data.department_director:
                    t_count = t_count + 1

            if 'secretary_management' in vals and vals['secretary_management']:
                t_count = t_count + 1
            elif 'secretary_management' not in vals:
                if data.secretary_management:
                    t_count = t_count + 1

            if 'candidate' in vals and vals['candidate']:
                t_count = t_count + 1
            elif 'candidate' not in vals:
                if data.candidate:
                    t_count = t_count + 1

            if t_count > 1:
                raise orm.except_orm(_('Errore'),
                                     _("Non è possibile impostare più di un ruolo!"))

        res = super(accreditation_roles, self).write(cr, uid, ids, vals, context=context)

        return res

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for ap in self.browse(cr, uid, ids):
            descr = ("%s") % (ap.description)
            res.append((ap.id, descr))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                                                context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}

        roles_list = []
        t_partner_id = None

        if context.get('default_user_id', False):
            t_user_id = context.get('default_user_id', False)
            user_data = self.pool.get('res.users').browse(cr, uid, t_user_id)
            t_partner_id = user_data.partner_id.id

        if context.get('default_partner_id', False):
            t_partner_id = context.get('default_partner_id', False)

        if t_partner_id:
            partner_obj = self.pool.get('res.partner')
            partner_data = partner_obj.browse(cr, uid, t_partner_id)
            for t_role_data in partner_data.roles_ids:
                if t_role_data.role_id and t_role_data.role_id.id not in roles_list:
                    roles_list.append(t_role_data.role_id.id)
            if partner_data.parent_id:
                for t_role_data in partner_data.parent_id.roles_ids:
                    if t_role_data.role_id and t_role_data.role_id.id not in roles_list:
                        roles_list.append(t_role_data.role_id.id)

        if roles_list:
            args = args + [['id', 'in', roles_list]]

        if name:
            req_ids = self.search(cr, uid, args +
                                  [('description', operator, name)],
                                  limit=limit,
                                  context=context)
        else:
            req_ids = self.search(cr, uid, args,
                                  limit=limit,
                                  context=context)
        return self.name_get(cr, uid, req_ids, context=context)
