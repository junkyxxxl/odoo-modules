# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Apulia Software S.r.l. (<info@apuliasoftware.it>)
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

from datetime import datetime
from dateutil.relativedelta import relativedelta


class calculate_ammortization_year(osv.osv_memory):

    _name = "calc.ammort.year"
    _description = "Calculate ammortization for period"

    _columns = {
        'fiscal_year': fields.many2one('account.fiscalyear', 'Fiscal Year',
                                       required=True),
        'date': fields.date('Amortization Date', required=True),
        'flag_all': fields.boolean(
            'All asset',
            help="If active keep all the assets in the selected category \
or only selected assets"),
        'flag_overw': fields.boolean(
            "Overwrite Existing", help="Overwrite existing calculate"),
        'category': fields.many2one('account.asset.category', 'Category'),
        }

    def calculate_ammortization(self, cr, uid, ids, context=None):
        param = self.browse(cr, uid, ids[0])
        asset = self.pool['account.asset.asset']
        if not context:
            context = {}
        if param.flag_all:
            filters = []
            if param.category:
                filters = [('category_id', '=', param.category.id)]
            ids_to_calc = asset.search(cr, uid, filters)
        else:
            if context['active_ids']:
                ids_to_calc = context['active_ids']
            else:
                raise osv.except_osv(
                    _('Error'),
                    _("Select almost one asset"))
        asset.calc_ammort(cr, uid, ids_to_calc, param.flag_overw,
                          param.fiscal_year, 'year', param.date, context)
        return {'type': 'ir.actions.act_window_close'}

    def delete_ammortization(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        param = self.browse(cr, uid, ids[0])
        asset_obj = self.pool['account.asset.asset']
        line_asset_obj = self.pool['account.asset.depreciation.line']
        line_ids = line_asset_obj.search(
            cr, uid, [('fiscal_year', '=', param.fiscal_year.id)])
        if line_ids:
            for line in line_asset_obj.browse(cr, uid, line_ids):
                if line.move_id:
                    raise osv.except_osv(
                        _('Error'),
                        _('There are account moves for asset %s' % (
                            line.asset_id.name)))
                if line.asset_id.last_use_year.id == param.fiscal_year.id:
                    year_before_id = self.calculate_period(cr, uid, ids)
                    if line.asset_id.first_use_year.id == param.fiscal_year.id:
                        asse = {'next_use_year': param.fiscal_year.id,
                                'last_use_year': False,
                                'type_amortization': line.type_amortization,
                                }
                    else:
                        asse = {'next_use_year': param.fiscal_year.id,
                                'last_use_year': year_before_id.id,
                                'type_amortization': line.type_amortization,
                                }
                    asset_obj.write(cr, uid, [line.asset_id.id, ], asse)
                    line_asset_obj.unlink(cr, uid, [line.id, ])
                else:
                    raise osv.except_osv(
                        _('Error'),
                        _("%s isn't the last year of use for asset %s" % (
                            param.fiscal_year.name, line.asset_id.name)))
        return {'type': 'ir.actions.act_window_close'}

    def calculate_period(self, cr, uid, ids, context=None):
        param = self.browse(cr, uid, ids[0])
        year_before = False
        fiscal_year = param.fiscal_year
        date_start = str(datetime.strptime(
            fiscal_year.date_start, '%Y-%m-%d')-relativedelta(years=1))[:10]
        date_stop = str(datetime.strptime(
            fiscal_year.date_stop, '%Y-%m-%d')-relativedelta(years=1))[:10]
        id_fy = self.pool.get('account.fiscalyear').search(cr, uid, [
            ('date_start', '=', date_start), ('date_stop', '=', date_stop)])
        if id_fy:
            year_before = self.pool['account.fiscalyear'].browse(cr, uid,
                                                                 id_fy[0])
        else:
            raise osv.except_osv(
                _('Error'),
                _("Impossibile to find previous year for period %s-%s" % (
                    date_start, date_stop)))
        return year_before
