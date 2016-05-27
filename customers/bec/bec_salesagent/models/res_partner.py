##############################################################################
#
#    Copyright (C) 2015 ISA srl (<http://www.isa.it>)
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
from openerp.exceptions import Warning
from openerp.tools.translate import _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _fnct_display_partner(self):
        self.fnct_not_display_partner = False
        if self.user_has_groups('base.group_becdata_own_salesperson'):
            if self.user_has_groups('base.group_becdata_allinfo'):
                self.fnct_not_display_partner = True
                if self.user_id and self.user_id.id == self._uid:
                    self.fnct_not_display_partner = False

    @api.one
    def _fnct_display_salesagent(self):
        self.fnct_not_display_salesagent = False
        if self.user_has_groups('base.group_becdata_own_salesperson'):
            if self.user_has_groups('base.group_becdata_allinfo'):
                self.fnct_not_display_salesagent = True
                if self.user_id and self.user_id.id == self._uid:
                    self.fnct_not_display_salesagent = False
                if self.user_has_groups('base.group_becdata_salesagent'):
                    self.fnct_not_display_salesagent = False

    fnct_not_display_partner = fields.Boolean(compute='_fnct_display_partner', string='Non Mostrare Info Partner')
    fnct_not_display_salesagent = fields.Boolean(compute='_fnct_display_salesagent', string='Non Mostrare Commerciale')

    @api.model
    def create(self, vals):
        if self.user_has_groups('base.group_becdata_own_salesperson'):
            raise Warning(_('Non hai i permessi per creare Clienti o Contatti.'))
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        for data in self:
            if data.user_has_groups('base.group_becdata_own_salesperson'):
                raise Warning(_('Non hai i permessi per modificare Clienti o Contatti.'))
        return super(ResPartner, self).write(vals)
