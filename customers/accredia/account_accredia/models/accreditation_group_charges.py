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

from openerp import fields, models, api


class AccreditationGroupCharges(models.Model):
    _name = 'accreditation.group.charges'
    _description = 'Scaglione per addebiti'

    name = fields.Char('Descrizione')
    invoiced_from = fields.Float('Fatturato Da Euro')
    invoiced_to = fields.Float('Fatturato A Euro')
    percentage = fields.Float('Percentuale di addebito')

    @api.model
    def create(self, vals):

        t_name = ''
        if 'invoiced_from' in vals:
            t_name += 'Da ' + str(vals['invoiced_from'] or 0)
        if 'invoiced_to' in vals:
            t_name += ' A ' + str(vals['invoiced_to'] or 0)
        if 'percentage' in vals:
            t_name += ' (% ' + str(vals['percentage']) + ')'
        vals.update({'name': t_name, })

        return super(AccreditationGroupCharges, self).create(vals)

    @api.multi
    def write(self, vals):

        t_name = ''
        if 'invoiced_from' in vals:
            t_name += 'Da ' + str(vals['invoiced_from'] or 0)
        elif self.invoiced_from or self.invoiced_from >= 0.0:
            t_name += 'Da ' + str(self.invoiced_from or 0)
        if 'invoiced_to' in vals:
            t_name += ' A ' + str(vals['invoiced_to'] or 0)
        elif self.invoiced_to or self.invoiced_to >= 0.0:
            t_name += ' A ' + str(self.invoiced_to or 0)
        if 'percentage' in vals:
            t_name += ' (% ' + str(vals['percentage'] or 0) + ')'
        elif self.percentage:
            t_name += ' (% ' + str(self.percentage or 0) + ')'
        vals.update({'name': t_name, })

        return super(AccreditationGroupCharges, self).write(vals)
