# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Giuseppe D'Alò (<g.dalo@apuliasoftware.it>)
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
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.osv import fields, osv
from openerp.tools.translate import _


class asset_depreciation_confirmation_wizard(osv.osv_memory):

    _inherit = "asset.depreciation.confirmation.wizard"


    _columns = {
        'at_day':fields.boolean('Calculate per days',help="compute the \
depreciation on the number of days from the beginning of year"),
        'to_day':fields.date('to date'),
        }

    def asset_compute(self, cr, uid, ids, context):
        data = self.browse(cr, uid, ids, context=context)
        context['at_day']=data[0].at_day
        if data[0].at_day:
            if not data[0].to_day:
                raise osv.except_osv(
                    _('Errore'),
                    _('To Date is mandatory for  calculate per day'))
        context['to_day']=data[0].to_day
        context['fiscal_year']= data[0].period_id.fiscalyear_id.id
        return super(asset_depreciation_confirmation_wizard,self).asset_compute(
            cr, uid, ids, context=context)

()
