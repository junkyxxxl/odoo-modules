# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class hr_accredia_changes_unit(orm.TransientModel):
    _name = 'hr.accredia.changes.unit'
    _description = 'Changes Sensible Information'
    _columns = {
        'unit_id': fields.many2one('accreditation.units', 'Unità'),
        'unit_code': fields.char('Unit Code',
                                 size=128,),
        'unit_name': fields.char('Unit Name',
                                 size=64),
        'location_id': fields.many2one('accreditation.locations',
                                       'Unit Locations'),
        'partner_id': fields.many2one('res.partner',
                                      'Ente'),
        'reason': fields.text("Reason"),
        'phone': fields.char('Phone',
                             size=50),
        'phone2': fields.char('2nd Phone',
                              size=50),
        'email': fields.char('Email',
                             size=120),
        'fax': fields.char('Fax',
                           size=50),
        'unit_category_id': fields.many2one('accreditation.units.categories',
                                            'Unit Category'),
        'registered_office': fields.boolean('Registered Office'),
        'validity_date': fields.date('Data Validità'),
    }

    def confirm(self, cr, uid, ids, context=None):
        unit_obj = self.pool.get('accreditation.units')
        unit_data = self.browse(cr, uid, ids[0])

        dict_unit = {'location_id': unit_data.location_id.id,
                     'phone': unit_data.phone or '',
                     'phone2': unit_data.phone2 or '',
                     'fax': unit_data.fax or '',
                     'email': unit_data.email or '',
                     'unit_category_id': unit_data.unit_category_id.id,
                     }
        new_unit_id = unit_obj.copy(cr, uid, unit_data.unit_id.id, context=None)
        unit_obj.write(cr, uid, new_unit_id, dict_unit)
        unit_obj.write(cr, uid, unit_data.unit_id.id, {'unit_changed': True})

        changelog_obj = self.pool.get('accreditation.unit.changelog')
        dict_changelog = {'authorized_user_id': uid,
                          'unit_id_old': unit_data.unit_id.id,
                          'unit_id_new': new_unit_id,
                          'comments': unit_data.reason,
                          'validity_date': unit_data.validity_date,
                          }
        changelog_obj.create(cr, uid, dict_changelog)

        return new_unit_id
