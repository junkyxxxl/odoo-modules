# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ISA s.r.l. (<http://www.isa.it>).
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

from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime


class WizardSetDate(models.TransientModel):
    _name = 'wizard.set.date'

    date = fields.Date('Data di inizio')
    phase_id = fields.Many2one('project.phase', string='Audit')

    @api.multi
    def do_set_date(self):
        self.ensure_one()
        if self.date:
            for user in self.phase_id.user_ids:
                user.date_start = self.date

                data_iniziale = datetime.strptime(self.date, '%Y-%m-%d')
                #Controllo se la data iniziale è sabato
                if data_iniziale.weekday() == 5:
                    data_iniziale = data_iniziale + relativedelta(days=2)
                #Controllo se la data iniziale è domenica
                if data_iniziale.weekday() == 6:
                    data_iniziale = data_iniziale + relativedelta(days=1)

                user.date_start = data_iniziale

                conta = 0
                data = data_iniziale
                while conta < (user.num_days-1):
                    data += relativedelta(days=1)
                    #Se la data non è compresa tra sabato e domenica, aggiorno conta
                    if data.weekday() not in (5, 6):
                        conta += 1
                user.date_end = data



