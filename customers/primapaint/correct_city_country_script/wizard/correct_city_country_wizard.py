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

from openerp import models, fields, api, _
from openerp.exceptions import Warning

class CorrectCountryCity(models.TransientModel):
    _name = 'wizard.correct.country.city'

    @api.one
    def correct_country_city(self):
        
        city_model = self.env['res.city']
        state_model = self.env['res.country.state']
        country_model = self.env['res.country']
        
        italy_id = country_model.search([('code','=','IT')])[0].id
        
        old_new_state = {}
        
        t_state_ids = state_model.search([('country_id','=',italy_id)])
        for state in t_state_ids:
            if state.code not in old_new_state:
                old_new_state[state.code] = []
            old_new_state[state.code].append(state.id)
            
        for on_st in old_new_state:
            old_new_state[on_st].sort()
            
        old_new_id = {}
        for on_st in old_new_state:
            old_new_id[old_new_state[on_st][1]] = old_new_state[on_st][0]
            
        for city in city_model.search([('country_id','=',italy_id)]):
            if city.state_id.id in old_new_id:
                city.write({'state_id':old_new_id[city.state_id.id]})
            
        return True