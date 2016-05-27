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


class accreditation_units(orm.Model):

    _name = "accreditation.units"
    _description = "Unita' operative"
    _rec_name = 'unit_name'

    def _get_replaced_by(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        changelog_obj = self.pool.get('accreditation.unit.changelog')
        for rec in self.browse(cr, uid, ids):
            res[rec.id] = None
            changelog_id = changelog_obj.search(cr, uid, [('unit_id_old', '=', rec.id)], limit=1)
            if changelog_id:
                t_changelog = changelog_obj.browse(cr, uid, changelog_id[0])
                res[rec.id] = t_changelog.unit_id_new.id
        return res

    def _get_replaces(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        changelog_obj = self.pool.get('accreditation.unit.changelog')
        for rec in self.browse(cr, uid, ids):
            res[rec.id] = None
            changelog_id = changelog_obj.search(cr, uid, [('unit_id_new', '=', rec.id)], limit=1)
            if changelog_id:
                t_changelog = changelog_obj.browse(cr, uid, changelog_id[0])
                res[rec.id] = t_changelog.unit_id_old.id
        return res

    def _get_unit_shortcut(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            res.setdefault(id, 0.0)        
        for unit in self.browse(cr, uid, ids, context=context):
            if (unit.unit_code and unit.unit_category_id.code and unit.unit_acronym and unit.location_id.province.code):
                res[unit.id] = unit.unit_code + "-" + unit.unit_category_id.code + "-" + unit.unit_acronym + "-" + unit.location_id.province.code
            else:
                res[unit.id] = unit.unit_code
        return res
   

    _columns = {
        'partner_id': fields.related('location_id',
                                     'partner_id',
                                     type='many2one',
                                     relation='res.partner',
                                     string='Partner'),

        'is_main': fields.related('unit_category_id',
                                  'is_main',
                                  type='boolean',
                                  readonly=True,
                                  string='Unità Principale'),
        'address': fields.related('location_id',
                                  'address',
                                  type='char',
                                  readonly=True,
                                  string='Indirizzo'),

        # Acronimo Unità
        'unit_acronym': fields.char('Acronimo Unità',
                                    size=50),
        'phone': fields.char('Phone',
                             size=50),
        'phone2': fields.char('2nd Phone',
                              size=50),
        'email': fields.char('Email',
                             size=120),
        'fax': fields.char('Fax',
                           size=50),
        'operating_unit': fields.boolean('Operating Unit'),
        'registered_office': fields.boolean('Registered Office'),

        'unit_name': fields.char('Unit Name', size=512),
        'name': fields.related('unit_name', type='char', string='Name'),

        'unit_code': fields.char('Unit Code',
                                 size=20),
                
        'unit_shortcut': fields.function(_get_unit_shortcut, type='char', store=True, string='Unit Shortcut'), 
           
        # Categoria Unit
        'unit_category_id': fields.many2one('accreditation.units.categories',
                                            'Unit Category'),
        # relazione (units->locations) many2one
        'location_id': fields.many2one('accreditation.locations',
                                       'Unit Locations'),
        # relazione (persons->units) many2many attraverso tabella persons_units
        'persons_ids': fields.one2many('accreditation.persons.units',
                                       'unit_id',
                                       'Unit Persons'),
        'active': fields.boolean('Active'),

        'unit_changed': fields.boolean('Unit Changed'),
        'replaced_by_id': fields.function(_get_replaced_by,
                                          type="many2one",
                                          relation="accreditation.units",
                                          string="Replaced By"),
        'replaces_id': fields.function(_get_replaces,
                                       type="many2one",
                                       relation="accreditation.units",
                                       string="Replaces"),
        'comment': fields.text('Comment')
        }

    _defaults = {
        'active': True,
        'unit_changed': False,
        }


    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for item in self.browse(cr, uid, ids, context=context):
            item_desc = (item.name or '') + ' - ' + (item.location_id.address or '') + '(' + (item.location_id.city or '') + ')'
            res.append((item.id, item_desc))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}

        t_filter = []

        if name:
            t_filter = ['|',
                        ('unit_acronym', operator, name),
                        ('unit_name', operator, name)]

        t_list = []
        if context.get('default_project_id', False):
            t_project_id = context.get('default_project_id', False)
            project_obj = self.pool.get('project.project')
            t_list.append(0)
            for unit_data in project_obj.browse(cr, uid, t_project_id).project_unit_ids:
                t_list.append(unit_data.id)

        if context.get('default_partner_id', False):
            t_partner_id = context.get('default_partner_id', False)
            partner_obj = self.pool.get('res.partner')
            partner_data = partner_obj.browse(cr, uid, t_partner_id)
            t_list.append(0)
            for main_unit_data in partner_data.main_units_ids:
                t_list.append(main_unit_data.id)

        if context.get('default_request_id', False):
            t_request_id = context.get('default_request_id', False)
            request_obj = self.pool.get('accreditation.request')
            t_list.append(0)
            partner_data = request_obj.browse(cr, uid, t_request_id).partner_id
            for main_unit_data in partner_data.main_units_ids:
                t_list.append(main_unit_data.id)

        if t_list:
            t_filter = t_filter + [['id', 'in', t_list]]

        t_filter = t_filter + args
        req_ids = self.search(cr, uid,
                              t_filter,
                              limit=limit,
                              context=context)
        return self.name_get(cr, uid, req_ids, context=context)

    def do_change_unit(self, cr, uid, ids, context):
        if context is None:
            context = {}

        unit_data = self.browse(cr, uid, ids[0], context)
        t_entity = unit_data.location_id.partner_id.id

        context.update({
            'default_unit_id': unit_data.id,
            'default_unit_name': unit_data.name or '',
            'default_unit_code': unit_data.unit_code or '',
            'default_location_id': unit_data.location_id and unit_data.location_id.id or None,
            'default_partner_id': t_entity,
            'default_phone': unit_data.phone or '',
            'default_phone2': unit_data.phone2 or '',
            'default_fax': unit_data.fax or '',
            'default_email': unit_data.email or '',
            'default_unit_category_id': unit_data.unit_category_id and unit_data.unit_category_id.id or None,
            })

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'hr_accredia',
                                              'view_hr_accredia_changes_unit_form')
        view_id = result and result[1] or False
        return {
            'name': _('Changes'),
            'res_model': 'hr.accredia.changes.unit',
            'type': 'ir.actions.act_window',
            'view_id': view_id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'target': 'new',
        }
