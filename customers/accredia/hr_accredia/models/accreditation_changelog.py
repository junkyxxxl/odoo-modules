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


class AccreditationChangelog(models.Model):
    _name = 'accreditation.changelog'
    _description = 'Log of Changes'

    authorized_user_id = fields.Many2one('res.users', 'User')
    partner_id_old = fields.Many2one('res.partner', 'Old Partner')
    partner_id_new = fields.Many2one('res.partner', 'New Partner')
    comments = fields.Text('Comments', translate=True)
    validity_date = fields.Date('Data Validità')
