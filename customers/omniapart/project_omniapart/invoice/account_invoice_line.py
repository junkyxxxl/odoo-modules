# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, orm
        
class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'
    
    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        if 'active_id' in context and 'active_model' in context and context['active_model'] == 'account.analytic.line':
            hr_analytic_obj = self.pool.get('hr.analytic.timesheet')
            work_obj = self.pool.get('project.task.work')
            product_obj = self.pool.get('product.product')
            
            hr_analytic_id = hr_analytic_obj.search(cr,uid,[('line_id','=',context['timesheet_id'])])          
            if hr_analytic_id:
                work_id = work_obj.search(cr,uid,[('hr_analytic_timesheet_id','=',hr_analytic_id)])
                if work_id:
                    work_data = work_obj.browse(cr,uid,work_id)
                    if 'product_id' in vals:
                        tmpl_data = product_obj.browse(cr,uid,vals['product_id']).product_tmpl_id
                        if tmpl_data.uos_id and tmpl_data.uos_coeff:
                            vals.update({'uos_id':tmpl_data.uos_id.id})
                            if 'price_unit' in vals:
                                vals.update({'price_unit':vals['price_unit']/tmpl_data.uos_coeff})
                            if work_data and work_data.hours:
                                vals.update({'quantity':work_data.task_id.planned_hours*tmpl_data.uos_coeff})

        return super(account_invoice_line, self).create(cr,uid,vals,context=context)
        