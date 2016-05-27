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

from openerp import models, api


class ResPartnerFiltraclienti(models.TransientModel):
    _inherit = 'res.partner.filtraclienti'

    @api.multi
    def set_domain(self):

        active_id = self.env.context.get('active_id', None)
        domain = self.get_domain_clienti()

        mass_mailing_obj = self.pool['mail.mass_mailing']
        mass_mailing_obj.write(self._cr, self._uid, active_id,
                               {'mailing_domain': domain,
                                'prev_mailing_domain': domain,
                                })

        return True
