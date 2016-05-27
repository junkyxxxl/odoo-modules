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


class ResCompany(models.Model):
    _inherit = 'res.company'

    price_min = fields.Float('Dir. Mantenimento Minimo', default=1500.0)

    fee_year = fields.Float('Quota Annua', default=1400.0)
    fee_year_small_lab = fields.Float('Quota Annua Piccolo Laboratorio', default=900.0)

    price_fixed_lab = fields.Float('Quota Fissa per Laboratorio accreditato', default=900.0)
    price_fixed_mer = fields.Float('Quota Fissa per Settore Metrologico', default=350.0)
