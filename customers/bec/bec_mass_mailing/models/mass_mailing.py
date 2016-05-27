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


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    def on_change_model_and_list(self, cr, uid, ids, mailing_model, list_ids, context=None):
        value = {}
        if mailing_model == 'mail.mass_mailing.contact':
            mailing_list_ids = set()
            for item in list_ids:
                if isinstance(item, (int, long)):
                    mailing_list_ids.add(item)
                elif len(item) == 3:
                    mailing_list_ids |= set(item[2])
            if mailing_list_ids:
                value['mailing_domain'] = "[('list_id', 'in', %s), ('opt_out', '=', False)]" % list(mailing_list_ids)
            else:
                value['mailing_domain'] = "[('list_id', '=', False)]"
        else:
            value['mailing_domain'] = []
        return {'value': value}

    @api.multi
    def set_domain(self):

        ctx = dict(self._context)
        ctx.update({'is_mass_mailing': True, })

        return {'type': 'ir.actions.act_window',
                'name': 'Mass Mailing: Imposta Filtri per il Partner',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'res.partner.filtraclienti',
                'context': ctx,
                'target': 'new',
                }

    prev_mailing_domain = fields.Char('Prev. Domain', default="[]")
