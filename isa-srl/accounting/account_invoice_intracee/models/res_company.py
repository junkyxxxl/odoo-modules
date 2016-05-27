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

from openerp import fields, models, api
from openerp.tools.translate import _


class AccountCeeServiceCodes(models.Model):

    _inherit = "res.company"

    # CodiceUA (codice utente abilitato) 4 alfa
    code_ua = fields.Char('Enabled User Code', size=4)

    # Periodicita flusso acquisto beni 1 alfa (M o T)
    period_purchase_goods = fields.Selection([('M', _('Monthly')),
                                              ('T', _('Quarterly')),
                                              ], 'Periodicity flow purchase goods',
                                             size=1)
    # Periodicita flusso acquisto servizi 1 alfa (M o T)
    period_purchase_services = fields.Selection([('M', _('Monthly')),
                                                 ('T', _('Quarterly')),
                                                 ], 'Periodicity flow purchase services',
                                                size=1)
    # Periodicita flusso cessione beni 1 alfa (M o T)
    period_disposals_goods = fields.Selection([('M', _('Monthly')),
                                               ('T', _('Quarterly')),
                                               ], 'Periodicity flow disposals goods',
                                              size=1)
    # Periodicita flusso cessione servizi 1 alfa (M o T)
    period_disposals_services = fields.Selection([('M', _('Monthly')),
                                                  ('T', _('Quarterly')),
                                                  ], 'Periodicity flow disposals services',
                                                 size=1)

    # Provincia destinazione
    province_destination = fields.Many2one('res.province', 'Province destination')
    # Partita Iva soggetto delegato
    vat_delegated_person = fields.Char('VAT delegated person', size=16)
    intracee_journal_id = fields.Many2one('account.journal', 'Sezionale Autofattura')
    intracee_giro_credit = fields.Many2one('account.journal', 'Sezionale Giroconto')
    intracee_fiscal_position = fields.Many2one('account.fiscal.position', 'Posizione Fiscale Autofattura')
    reverse_charge_journal_id = fields.Many2one('account.journal', 'Sezionale Autofattura')
    reverse_charge_giro_credit = fields.Many2one('account.journal', 'Sezionale Giroconto')
    reverse_charge_fiscal_position = fields.Many2one('account.fiscal.position', 'Posizione Fiscale Giroconto')

    @api.multi
    def onchange_intracee_journal_id(self, intracee_journal_id=False):
        warning = {}
        if intracee_journal_id:
            journal_data = self.env['account.journal'].browse(intracee_journal_id)
            if not journal_data.iva_registry_id:
                warning = {'title': _('Warning!'),
                           'message': _(('Before validating an invoice you have to link %s with a VAT registry!')) % (journal_data.name)
                           }
        return {'value': {}, 'warning': warning, }

    @api.multi
    def onchange_intracee_giro_credit(self, intracee_giro_credit=False):
        warning = {}
        if intracee_giro_credit:
            journal_data = self.env['account.journal'].browse(intracee_giro_credit)
            if journal_data.iva_registry_id:
                warning = {'title': _('Warning!'),
                           'message': _(('Journal %s should not be linked with a VAT registry!')) % (journal_data.name)
                           }
        return {'value': {}, 'warning': warning, }
