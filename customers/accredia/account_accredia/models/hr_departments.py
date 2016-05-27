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

from openerp import fields, models
import openerp.addons.decimal_precision as dp


class HrDepartment(models.Model):
    # Department
    _inherit = 'hr.department'

    sale_journal_id = fields.Many2one('account.journal', 'Sale Journal')
    purchase_journal_id = fields.Many2one('account.journal', 'Purchase Journal')
    product_debit = fields.Many2one('product.product', 'Articolo per addebito')
    annual_fee_for_debit = fields.Float('Quota annuale per addebito', digits_compute=dp.get_precision('Account'))
    product_charged_in_advance = fields.Many2one('product.product', 'Articolo per addebito in acconto')
    product_debit_balance = fields.Many2one('product.product', 'Articolo per addebito a saldo')
    minimum_quota = fields.Float('Quota minima', digits_compute=dp.get_precision('Account'))
    group_for_charges_id = fields.Many2one('accreditation.group.charges', 'Scaglione per addebiti')
    product_debit = fields.Many2one('product.product', 'Articolo per addebito')
    amount_first_rule_accredited = fields.Float('Importo per la prima Direttiva/Regolamento accreditato',
                                                digits_compute=dp.get_precision('Account'))
    amount_subsequent_accreditation = fields.Float('Importo per ogni accreditamento successivo',
                                                   digits_compute=dp.get_precision('Account'))
    product_annual_quota_maintenance = fields.Many2one('product.product',
                                                       'Articolo quota annua diritto di mantenimento')
    product_annual_quota_maintenance_small_labs = fields.Many2one('product.product',
                                                                  'Articolo quota annua diritto di mantenimento per piccoli laboratori')
    product_fixed_fee_accredited_laboratory = fields.Many2one('product.product',
                                                              'Articolo quota fissa per ogni laboratorio accreditato')
    product_fee_accredited_accredited_metrology = fields.Many2one('product.product',
                                                                  'Articolo quota per ogni settore metrologico accreditato')
    maintenance_rights_journal_id = fields.Many2one('account.journal', 'Sezionale Diritti Mantenimento')
