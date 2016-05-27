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

from openerp import fields, models


class AccreditationUnitChangelog(models.Model):
    _name = 'accreditation.unit.changelog'
    _description = 'Log of Changes For Accreditation Units'

    authorized_user_id = fields.Many2one('res.users', 'User')
    unit_id_old = fields.Many2one('accreditation.units', 'Old Unit')
    unit_id_new = fields.Many2one('accreditation.units', 'New Unit')
    comments = fields.Text('Comments', translate=True)
    validity_date = fields.Date('Data Validità')
