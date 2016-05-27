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

import time
from openerp.osv import orm, fields
from openerp.tools.translate import _
import logging


_logger = logging.getLogger('Debug:')

class account_analytic_line(orm.Model):
    _inherit = 'account.analytic.line'

    def _get_worked_unit_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        task_obj = self.pool.get('project.task.work')
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        for id in ids:
            timesheet_id = timesheet_obj.search(cr,uid,[('line_id','=',id)])
            if timesheet_id:
                task_id = task_obj.search(cr,uid,[('hr_analytic_timesheet_id','in',timesheet_id)])
                if task_id:         
                    hours = task_obj.browse(cr,uid,task_id).task_id.effective_hours           
                    res[id] = hours
            else:
                res[id] = False
        return res
    
    _columns = {
        'zig': fields.related('account_id','zig',type='char',string="ZIG"),
        'c_number': fields.related('account_id','c_number',type='char',string='Riferimento Contratto Cliente'),
        'worked_unit_amount':fields.function(_get_worked_unit_amount, type='float', string='Ore lavorate'),    
        'partner_id': fields.related('account_id','partner_id',type='many2one',relation='res.partner',string='Partner',store=True),
        'prospect_id': fields.related('account_id','prospect_id',type='many2one',relation='res.partner',string='Prospect', store=True),                        
        }    

    def _get_invoice_price(self, cr, uid, account, product_id, user_id, qty, context = {}):
        for grid in account.user_product_ids:
            
            if 'activity_date' in context:
                if grid.user_id.id==user_id:   
                    date_to = grid.date_to or False
                    date_from = grid.date_from or False
                    date = context['activity_date'] or False

                    if not date or (not date_to and not date_from) or (date_to and not date_from and date <= date_to) or (not date_to and date_from and date >= date_to) or (date_to and date_from and date >= date_from and date <= date_to):                
                        return grid.price
                    
        return super(account_analytic_line, self)._get_invoice_price(cr, uid, account, product_id, user_id, qty, context)    

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        if ('task_id' in context and context['task_id']) or ids:
            if 'task_id' in context and context['task_id']:
                l_id = context['task_id']
            else:
                if isinstance(ids, list):
                    l_id = ids[0]
                else:
                    l_id = ids
                               
                work_obj = self.pool.get('project.task.work')
                timesheet_obj = self.pool.get('hr.analytic.timesheet')
                timesheet_id = timesheet_obj.search(cr,uid,[('line_id','=',l_id)])
                if timesheet_id:
                    task_id = work_obj.search(cr,uid,[('hr_analytic_timesheet_id','in',timesheet_id)])
                    if task_id: 
                        l_id = work_obj.browse(cr, uid, task_id).task_id.id
            activity_data = self.browse(cr, uid, ids)

            task_obj = self.pool.get('project.task')
            task_data = task_obj.browse(cr, uid, l_id)
            
            try:
                project_data = task_data.project_id
            except:
                return super(account_analytic_line,self).write(cr, uid, ids, vals,context=context)
            
            contract_data = project_data.analytic_account_id

            for line in contract_data.user_product_ids:
                if line.user_id == activity_data.user_id and line.product_id:
                    date_to = line.date_to or False
                    date_from = line.date_from or False
                    date = activity_data.date or False
                    if not date or (not date_to and not date_from) or (date_to and not date_from and date <= date_to) or (not date_to and date_from and date >= date_to) or (date_to and date_from and date >= date_from and date <= date_to):
                        vals.update({'product_id':line.product_id.id})
                        if line.product_id.property_account_expense:
                            vals.update({'general_account_id':line.product_id.property_account_expense.id})
                        vals.update({'unit_amount':task_data.planned_hours})
                        if 'task_id' in context:
                            vals.update({'amount':- activity_data.unit_amount*line.product_id.standard_price})
                        else:
                            vals.update({'amount':- (task_data.planned_hours-task_data.remaining_hours)*line.product_id.standard_price})
                        break
        return super(account_analytic_line,self).write(cr, uid, ids, vals, context=context)

    def invoice_cost_create(self, cr, uid, ids, data=None, context=None):
        analytic_account_obj = self.pool.get('account.analytic.account')
        account_payment_term_obj = self.pool.get('account.payment.term')
        invoice_obj = self.pool.get('account.invoice')
        product_obj = self.pool.get('product.product')
        invoice_factor_obj = self.pool.get('hr_timesheet_invoice.factor')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        product_uom_obj = self.pool.get('product.uom')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoices = []
        if context is None:
            context = {}
        if data is None:
            data = {}

        journal_types = {}

        # prepare for iteration on journal and accounts
        for line in self.pool.get('account.analytic.line').browse(cr, uid, ids, context=context):
            if line.journal_id.type not in journal_types:
                journal_types[line.journal_id.type] = set()
            journal_types[line.journal_id.type].add((line.account_id.partner_id, line.account_id.company_id, line.account_id.pricelist_id))
        for journal_type, keys in journal_types.items():
            for key in keys:
                if (not key[0]) or not (key[1] or not (key[2])):
                    raise orm.except_orm(_('Analytic Account Incomplete!'),
                            _('Contract incomplete. Please fill in the Customer, the Company and Pricelist fields.'))
                
                partner = key[0]
                company = key[1]
                pricelist = key[2]
                
                date_due = False
                if partner.property_payment_term:
                    pterm_list= account_payment_term_obj.compute(cr, uid,
                            partner.property_payment_term.id, value=1,
                            date_ref=time.strftime('%Y-%m-%d'))
                    if pterm_list:
                        pterm_list = [line[0] for line in pterm_list]
                        pterm_list.sort()
                        date_due = pterm_list[-1]

                curr_invoice = {
                    'name': time.strftime('%d/%m/%Y') + ' - '+partner.name,
                    'partner_id': partner.id,
                    'company_id': company.id,
                    'payment_term': partner.property_payment_term.id or False,
                    'account_id': partner.property_account_receivable.id,
                    'currency_id': pricelist.currency_id.id,
                    'date_due': date_due,
                    'fiscal_position': partner.property_account_position.id
                }
                _logger.info('Data is %s' %(data))
                if data.get('date_invoice',False):
                    curr_invoice.update({'date_invoice': data.get('date_invoice')})

                # VAT X CASH OVERRIDE
                data_journal_id = data.get('journal_id', False)
                if data_journal_id:
                    curr_invoice.update({'journal_id': data_journal_id[0]})
                fpos_id = data.get('fpos_id', False)
                if fpos_id:
                    curr_invoice.update({
                        'fiscal_position': fpos_id[0]})
                # --- VAT X CASH OVERRIDE
                                    
                context2 = context.copy()
                context2['lang'] = partner.lang
                # set company_id in context, so the correct default journal will be selected
                context2['force_company'] = curr_invoice['company_id']
                # set force_company in context so the correct product properties are selected (eg. income account)
                context2['company_id'] = curr_invoice['company_id']

                last_invoice = invoice_obj.create(cr, uid, curr_invoice, context=context2)
                invoices.append(last_invoice)

                cr.execute("""  SELECT line.product_id, line.user_id, line.to_invoice, sum(line.amount), sum(line.unit_amount), line.product_uom_id, line.id
                                FROM account_analytic_line as line, account_analytic_journal journal, account_analytic_account as analytic
                                WHERE 
                                    line.account_id = analytic.id AND
                                    analytic.partner_id = %s AND
                                    analytic.company_id = %s AND
                                    analytic.pricelist_id = %s AND
                                    line.id IN %s AND 
                                    journal.type = %s AND 
                                    line.to_invoice IS NOT NULL AND
                                    line.journal_id = journal.id
                                GROUP BY line.product_id, line.user_id, line.to_invoice, line.product_uom_id, line.id, analytic.name
                                ORDER BY analytic.name""", (partner.id, company.id, pricelist.id, tuple(ids), journal_type))
                tmp = cr.fetchall()
                for product_id, user_id, factor_id, total_price, qty, uom, id in tmp:
                    account = self.browse(cr,uid,id).account_id
                    activity_date = self.browse(cr,uid,id).date or False
                    context2.update({'uom': uom, 'activity_date': activity_date})

                    if data.get('product'):
                        # force product, use its public price
                        product_id = data['product'][0]
                        unit_price = self._get_invoice_price(cr, uid, account, product_id, user_id, qty, context2)
                    elif journal_type == 'general' and product_id:
                        # timesheets, use sale price
                        unit_price = self._get_invoice_price(cr, uid, account, product_id, user_id, qty, context2)
                    else:
                        # expenses, using price from amount field
                        unit_price = total_price*-1.0 / qty

                    factor = invoice_factor_obj.browse(cr, uid, factor_id, context=context2)
                    # factor_name = factor.customer_name and line_name + ' - ' + factor.customer_name or line_name
                    factor_name = factor.customer_name
                    curr_line = {
                        'price_unit': unit_price,
                        'quantity': qty,
                        'product_id': product_id or False,
                        'discount': factor.factor,
                        'invoice_id': last_invoice,
                        'name': factor_name,
                        'uos_id': uom,
                        'account_analytic_id': account.id,
                    }
                    product = product_obj.browse(cr, uid, product_id, context=context2)
                    if product:
                        factor_name = product_obj.name_get(cr, uid, [product_id], context=context2)[0][1]
                        if factor.customer_name:
                            factor_name += ' - ' + factor.customer_name

                        general_account = product.property_account_income or product.categ_id.property_account_income_categ
                        if not general_account:
                            raise orm.except_orm(_("Configuration Error!"), _("Please define income account for product '%s'.") % product.name)
                        taxes = product.taxes_id or general_account.tax_ids
                        # VAT X CASH OVERRIDE
                        fpos_data = data.get('fpos_id', False)
                        if fpos_data:
                            fpos = fiscal_pos_obj.browse(cr, uid,
                                                         fpos_data[0], context)
                        else:
                            fpos = account.partner_id.property_account_position
                        # ---- VAT X CASH OVERRIDE
                        tax = fiscal_pos_obj.map_tax(cr, uid, fpos, taxes)
                        curr_line.update({
                            'invoice_line_tax_id': [(6, 0, tax)],
                            'name': factor_name,
                            'invoice_line_tax_id': [(6, 0, tax)],
                            'account_id': general_account.id,
                        })
                    #
                    # Compute for lines
                    #
                    cr.execute("SELECT * FROM account_analytic_line WHERE account_id = %s and id = %s AND product_id=%s and to_invoice=%s ORDER BY account_analytic_line.account_id, account_analytic_line.date", (account.id, id, product_id, factor_id))

                    line_ids = cr.dictfetchall()
                    note = []
                    for line in line_ids:
                        # set invoice_line_note
                        details = []
                        
                        if data.get('contract', False) and line['account_id']:
                            details.append(analytic_account_obj.browse(cr,uid,line['account_id']).name)
                                                    
                        if data.get('task', False):
                            hr_obj = self.pool.get('hr.analytic.timesheet')
                            work_obj = self.pool.get('project.task.work')

                            hr_analytic_id = hr_obj.search(cr, uid, [('line_id', '=', id)])
                            if hr_analytic_id:
                                work_id = work_obj.search(cr, uid, [('hr_analytic_timesheet_id', 'in', hr_analytic_id)])
                                if work_id:
                                    work_data = work_obj.browse(cr, uid, work_id)
                                    details.append(work_data.task_id.name)

                        if data.get('date', False):
                            details.append(line['date'])
                        if data.get('time', False):
                            if line['product_uom_id']:
                                details.append("%s %s" % (line['unit_amount'], product_uom_obj.browse(cr, uid, [line['product_uom_id']],context2)[0].name))
                            else:
                                details.append("%s" % (line['unit_amount'], ))
                        if data.get('name', False):
                            details.append(line['name'])
                        if details:    
                            note.append(u' - '.join(map(lambda x: unicode(x) or '',details)))
                    if note:
                        if data.get('task', False):
                            curr_line['name'] = ""
                        else:
                            curr_line['name']+="\n"
                        curr_line['name'] += ("\n".join(map(lambda x: unicode(x) or '',note)))
                    context.update({'timesheet_id':id})
                    invoice_line_obj.create(cr, uid, curr_line, context=context)
                    cr.execute("update account_analytic_line set invoice_id=%s WHERE account_id = %s and id IN %s", (last_invoice, account.id, tuple(ids)))
                    self.invalidate_cache(cr, uid, ['invoice_id'], ids, context=context)

                invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
        return invoices
