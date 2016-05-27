# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import datetime
import time
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import api


class ResPartner(orm.Model):
    _inherit = "res.partner"

    def do_reload_followup(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        if context.get('date_ref', False):
            t_date = context.get('date_ref', False)
            context.update({'default_date': t_date,
                            })

        if context.get('default_dom_department_id', False):
            t_dep = context.get('default_dom_department_id', False)
            context.update({'default_department_id': t_dep,
                            })

        if ids:
            context.update({'default_partner_id': ids[0],
                            })

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_accredia',
                                              'view_account_followup_date')
        view_id = result and result[1] or False

        return {
            'name': _('Solleciti per Data'),
            'view_type': 'form',
            'context': context,
            'view_id': view_id,
            'view_mode': 'form',
            'res_model': 'account_followup.date',
            'type': 'ir.actions.act_window',
            'target': 'new',
            }

    def do_update_followup_level(self, cr, uid, to_update, partner_list, date, context=None):
        # update the follow-up level on account.move.line
        for id in to_update.keys():

            self.pool.get('account.move.line').write(cr, uid, [int(id)], {'followup_line_id': to_update[id]['level'], 
                                                                          'followup_date': date})

    def do_partner_print2(self, cr, uid, wizard_partner_ids, data, context=None):
        if context is None:
            context = {}
        # wizard_partner_ids are ids from special view, not from res.partner
        if not wizard_partner_ids:
            return {}
        data['partner_ids'] = wizard_partner_ids
        datas = {
             'ids': [],
             'model': 'account_followup.followup',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_followup.followup.print2',
            'datas': datas,
            'context': context,
            }

    def do_button_print(self, cr, uid, ids, context=None):
        assert(len(ids) == 1)

        t_date = fields.date.context_today(self, cr, uid, context=context)
        if context.get('date_ref', False):
            t_date = context.get('date_ref', False)

        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        # search if the partner has accounting entries to print. If not, it may not be present in the
        # psql view the report is based on, so we need to stop the user here.
        t_res_ids = self.pool.get('account.move.line').search(cr, uid, [
                                                                   ('partner_id', '=', ids[0]),
                                                                   ('account_id.type', '=', 'receivable'),
                                                                   ('reconcile_id', '=', False),
                                                                   ('state', '!=', 'draft'),
                                                                   ('company_id', '=', company_id),
                                                                  ], context=context)
        if not t_res_ids:
            raise orm.except_orm(_('Error!'),_("The partner does not have any accounting entries to print in the overdue report for the current company."))

        t_res_ids = self.pool.get('account.move.line').search(cr, uid, [('blocked', '!=', True),
                                                                   ('partner_id', '=', ids[0]),
                                                                   ('account_id.type', '=', 'receivable'),
                                                                   ('reconcile_id', '=', False),
                                                                   ('state', '!=', 'draft'),
                                                                   ('company_id', '=', company_id),
                                                                  ], context=context)
        if not t_res_ids:
            raise orm.except_orm(_('Error!'),_("The partner does not have any accounting entries to print in the overdue report for the current company."))

        self.message_post(cr, uid, [ids[0]], body=_('Printed overdue payments report'), context=context)
        #build the id of this partner in the psql view. Could be replaced by a search with [('company_id', '=', company_id),('partner_id', '=', ids[0])]
        wizard_partner_ids = [ids[0] * 10000 + company_id]
        followup_ids = self.pool.get('account_followup.followup').search(cr, uid, [('company_id', '=', company_id)], context=context)
        if not followup_ids:
            raise orm.except_orm(_('Error!'),_("There is no followup plan defined for the current company."))
        data = {
            'date': t_date,
            'followup_id': followup_ids[0],
        }

        #Get partners
        cr.execute(
            "SELECT l.partner_id, l.followup_line_id,l.date_maturity, l.date, l.id "\
            "FROM account_move_line AS l "\
                "LEFT JOIN account_account AS a "\
                "ON (l.account_id=a.id) "\
            "WHERE (l.reconcile_id IS NULL) "\
                "AND (a.type='receivable') "\
                "AND (l.state<>'draft') "\
                "AND (l.partner_id = " + str(ids[0]) + ") "\
                "AND (a.active) "\
                "AND (l.debit > 0) "\
                "AND (l.company_id = %s) " \
                "AND (l.blocked = False)" \
            "ORDER BY l.date", (company_id,))  #l.blocked added to take litigation into account and it is not necessary to change follow-up level of account move lines without debit
        move_lines = cr.fetchall()

        old = None
        fups = {}
        fup_id = followup_ids[0]

        cr.execute(
            "SELECT * "\
            "FROM account_followup_followup_line "\
            "WHERE followup_id=%s "\
            "ORDER BY delay", (fup_id,))

        current_date = datetime.date(*time.strptime(t_date,
            '%Y-%m-%d')[:3])
        #Create dictionary of tuples where first element is the date to compare with the due date and second element is the id of the next level
        for result in cr.dictfetchall():
            delay = datetime.timedelta(days=result['delay'])
            fups[old] = (current_date - delay, result['id'])
            old = result['id']

        partner_list = []
        to_update = {}

        for partner_id, followup_line_id, date_maturity,date, id in move_lines:
            if followup_line_id not in fups:
                continue
            stat_line_id = partner_id * 10000 + company_id
            if date_maturity:
                if date_maturity <= fups[followup_line_id][0].strftime('%Y-%m-%d'):
                    if stat_line_id not in partner_list:
                        partner_list.append(stat_line_id)
                    to_update[str(id)]= {'level': fups[followup_line_id][1], 'partner_id': stat_line_id}
            elif date and date <= fups[followup_line_id][0].strftime('%Y-%m-%d'):
                if stat_line_id not in partner_list:
                    partner_list.append(stat_line_id)
                to_update[str(id)]= {'level': fups[followup_line_id][1], 'partner_id': stat_line_id}

        #Update partners
        self.do_update_followup_level(cr, uid, to_update, ids, t_date, context=context)

        # send email
        self.do_partner_mail(cr, uid, ids, context=context)

        # action done
        partners_to_clear = []
        for part in self.browse(cr, uid, ids, context=context): 
            if not part.unreconciled_aml_ids: 
                partners_to_clear.append(part.id)
        self.action_done(cr, uid, partners_to_clear, context=context)

        #call the print overdue report on this partner
        return self.do_partner_print2(cr, uid, wizard_partner_ids, data, context=context)

    def do_partner_manual_action(self, cr, uid, partner_ids, context=None): 
        #partner_ids -> res.partner
        for partner in self.browse(cr, uid, partner_ids, context=context):
            #Check action: check if the action was not empty, if not add
            action_text= ""
            if partner.payment_next_action:
                action_text = (partner.payment_next_action or '') + "\n" + (partner.latest_followup_level_id_without_lit.manual_action_note or '')
            else:
                action_text = partner.latest_followup_level_id_without_lit.manual_action_note or ''

            #Check date: only change when it did not exist already
            t_date = fields.date.context_today(self, cr, uid, context=context)
            if context.get('date_ref', False):
                t_date = context.get('date_ref', False)
            action_date = partner.payment_next_action_date or t_date

            # Check responsible: if partner has not got a responsible already, take from follow-up
            responsible_id = False
            if partner.payment_responsible_id:
                responsible_id = partner.payment_responsible_id.id
            else:
                p = partner.latest_followup_level_id_without_lit.manual_action_responsible_id
                responsible_id = p and p.id or False
            self.write(cr, uid, [partner.id], {'payment_next_action_date': action_date,
                                        'payment_next_action': action_text,
                                        'payment_responsible_id': responsible_id})

    @api.cr_uid_ids_context
    def do_partner_mail(self, cr, uid, partner_ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['followup'] = True
        #partner_ids are res.partner ids
        # If not defined by latest follow-up level, it will be the default template if it can find it
        mtp = self.pool.get('email.template')
        unknown_mails = 0
        for partner in self.browse(cr, uid, partner_ids, context=ctx):
            partners_to_email = [child for child in partner.child_ids if child.type == 'invoice' and child.email]
            if not partners_to_email and partner.email:
                partners_to_email = [partner]
            if partners_to_email:
                level = partner.latest_followup_level_id_without_lit
                for partner_to_email in partners_to_email:
                    if level and level.send_email and level.email_template_id and level.email_template_id.id:
                        mtp.send_mail(cr, uid, level.email_template_id.id, partner_to_email.id, context=ctx)
                    else:
                        mail_template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid,
                                                        'account_followup', 'email_template_account_followup_default')
                        mtp.send_mail(cr, uid, mail_template_id[1], partner_to_email.id, context=ctx)
                if partner not in partners_to_email:
                    self.message_post(cr, uid, [partner.id], body=_('Overdue email sent to %s' % ', '.join(['%s <%s>' % (partner.name, partner.email) for partner in partners_to_email])), context=context)
            else:
                unknown_mails = unknown_mails + 1
                action_text = _("Email not sent because of email address of partner not filled in")
                t_date = fields.date.context_today(self, cr, uid, context=ctx)
                if context.get('date_ref', False):
                    t_date = context.get('date_ref', False)
                if partner.payment_next_action_date:
                    payment_action_date = min(t_date, partner.payment_next_action_date)
                else:
                    payment_action_date = t_date
                if partner.payment_next_action:
                    payment_next_action = partner.payment_next_action + " \n " + action_text
                else:
                    payment_next_action = action_text
                self.write(cr, uid, [partner.id], {'payment_next_action_date': payment_action_date,
                                                   'payment_next_action': payment_next_action}, context=ctx)
        return unknown_mails

    def get_followup_table_html(self, cr, uid, ids, context=None):
        """ Build the html tables to be included in emails send to partners,
            when reminding them their overdue invoices.
            :param ids: [id] of the partner for whom we are building the tables
            :rtype: string
        """
        from ..report import account_followup_print

        assert len(ids) == 1
        if context is None:
            context = {}
        partner = self.browse(cr, uid, ids[0], context=context)
        #copy the context to not change global context. Overwrite it because _() looks for the lang in local variable 'context'.
        #Set the language to use = the partner language
        context = dict(context, lang=partner.lang)
        followup_table = ''
        if partner.unreconciled_aml_ids:
            company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
            t_date = fields.date.context_today(self, cr, uid, context=context)
            if context.get('date_ref', False):
                t_date = context.get('date_ref', False)
            current_date = t_date
            rml_parse = account_followup_print.report_rappel2(cr, uid, "followup_rml_parser")
            final_res = rml_parse._lines_get_with_partner(partner, company.id)

            for currency_dict in final_res:
                currency = currency_dict.get('line', [{'currency_id': company.currency_id}])[0]['currency_id']
                followup_table += '''
                <table border="2" width=100%%>
                <tr>
                    <td>''' + _("Invoice Date") + '''</td>
                    <td>''' + _("Description") + '''</td>
                    <td>''' + _("Reference") + '''</td>
                    <td>''' + _("Due Date") + '''</td>
                    <td>''' + _("Amount") + " (%s)" % (currency.symbol) + '''</td>
                    <td>''' + _("Lit.") + '''</td>
                </tr>
                ''' 
                total = 0
                for aml in currency_dict['line']:
                    block = aml['blocked'] and 'X' or ' '
                    total += aml['balance']
                    strbegin = "<TD>"
                    strend = "</TD>"
                    date = aml['date_maturity'] or aml['date']
                    if date <= current_date and aml['balance'] > 0:
                        strbegin = "<TD><B>"
                        strend = "</B></TD>"
                    followup_table +="<TR>" + strbegin + str(aml['date']) + strend + strbegin + aml['name'] + strend + strbegin + (aml['ref'] or '') + strend + strbegin + str(date) + strend + strbegin + str(aml['balance']) + strend + strbegin + block + strend + "</TR>"

                total = rml_parse.formatLang(total, dp='Account', currency_obj=currency)
                followup_table += '''<tr> </tr>
                                </table>
                                <center>''' + _("Amount due") + ''' : %s </center>''' % (total)
        return followup_table

    def _get_amounts_and_date(self, cr, uid, ids, name, arg, context=None):
        '''
        Function that computes values for the followup functional fields. Note that 'payment_amount_due'
        is similar to 'credit' field on res.partner except it filters on user's company.
        '''
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        current_date = fields.date.context_today(self, cr, uid, context=context)
        if context.get('date_ref', False):
            current_date = context.get('date_ref', False)

        for partner in self.browse(cr, uid, ids, context=context):
            worst_due_date = False
            amount_due = amount_overdue = 0.0
            for aml in partner.unreconciled_aml_ids:
                if (aml.company_id == company):
                    date_maturity = aml.date_maturity or aml.date
                    if not worst_due_date or date_maturity < worst_due_date:
                        worst_due_date = date_maturity
                    amount_due += aml.result
                    if (date_maturity <= current_date):
                        amount_overdue += aml.result
            res[partner.id] = {'payment_amount_due': amount_due, 
                               'payment_amount_overdue': amount_overdue, 
                               'payment_earliest_due_date': worst_due_date}
        return res

    def _get_followup_overdue_query(self, cr, uid, args, overdue_only=False, context=None):
        '''
        This function is used to build the query and arguments to use when making a search on functional fields
            * payment_amount_due
            * payment_amount_overdue
        Basically, the query is exactly the same except that for overdue there is an extra clause in the WHERE.

        :param args: arguments given to the search in the usual domain notation (list of tuples)
        :param overdue_only: option to add the extra argument to filter on overdue accounting entries or not
        :returns: a tuple with
            * the query to execute as first element
            * the arguments for the execution of this query
        :rtype: (string, [])
        '''
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        having_where_clause = ' AND '.join(map(lambda x: '(SUM(bal2) %s %%s)' % (x[1]), args))
        having_values = [x[2] for x in args]
        query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)

        overdue_only_str = ''
        if overdue_only:
            overdue_only_str = 'AND date_maturity <= NOW()'
            if context.get('date_ref', False):
                overdue_only_str = "AND date_maturity <= '" + context.get('date_ref', False) + "'"

        t_deparment_str = ''
        if context.get('default_dom_department_id', False):
            t_deparment_id = context.get('default_dom_department_id', False)
            if t_deparment_id:
                t_deparment_str = "AND j.department_id = '" + str(t_deparment_id) + "'"

        res_query = ('''SELECT pid AS partner_id, SUM(bal2) FROM
                    (SELECT CASE WHEN bal IS NOT NULL THEN bal
                    ELSE 0.0 END AS bal2, p.id as pid FROM
                    (SELECT (debit-credit) AS bal, l.partner_id
                    FROM account_move_line l
                         JOIN account_move am ON l.move_id = am.id
                         JOIN account_journal j ON j.id = am.journal_id
                    WHERE account_id IN
                            (SELECT id FROM account_account
                            WHERE type=\'receivable\' AND active)
                    ''' + overdue_only_str + '''
                    ''' + t_deparment_str + '''
                    AND reconcile_id IS NULL
                    AND l.company_id = %s
                    AND ''' + query + ''') AS l
                    RIGHT JOIN res_partner p
                    ON p.id = partner_id ) AS pl
                    GROUP BY pid HAVING ''' + having_where_clause, [company_id] + having_values)
        return res_query

    def _payment_overdue_search(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        query, query_args = self._get_followup_overdue_query(cr, uid, args, overdue_only=True, context=context)
        cr.execute(query, query_args)
        res = cr.fetchall()
        if not res:
            return [('id','=','0')]
        return [('id','in', [x[0] for x in res])]

    def _payment_earliest_date_search(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        having_where_clause = ' AND '.join(map(lambda x: '(MIN(l.date_maturity) %s %%s)' % (x[1]), args))
        having_values = [x[2] for x in args]
        query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)
        cr.execute('SELECT partner_id FROM account_move_line l '\
                    'WHERE account_id IN '\
                        '(SELECT id FROM account_account '\
                        'WHERE type=\'receivable\' AND active) '\
                    'AND l.company_id = %s '
                    'AND reconcile_id IS NULL '\
                    'AND '+query+' '\
                    'AND partner_id IS NOT NULL '\
                    'GROUP BY partner_id HAVING '+ having_where_clause,
                     [company_id] + having_values)
        res = cr.fetchall()
        if not res:
            return [('id','=','0')]
        return [('id','in', [x[0] for x in res])]

    def _payment_due_search(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        query, query_args = self._get_followup_overdue_query(cr, uid, args, overdue_only=False, context=context)
        cr.execute(query, query_args)
        res = cr.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]

    def _get_dom_department_id(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):

            res[partner.id] = None
            if context.get('default_dom_department_id', False):
                res[partner.id] = context.get('default_dom_department_id', False)

        return res

    def _get_dom_date(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):

            res[partner.id] = None
            if context.get('default_dom_date', False):
                res[partner.id] = context.get('default_dom_date', False)

        return res

    def _get_unreconciled_aml_ids(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}

        t_deparment_id = None
        if context.get('default_dom_department_id', False):
            t_deparment_id = context.get('default_dom_department_id', False)

        for partner in self.browse(cr, uid, ids, context=context):
            result[partner.id] = []
            for aml in partner.unreconciled_aml_ids:
                if aml.blocked is not True and aml.department_id and aml.department_id.id == t_deparment_id:
                    result[partner.id].append(aml.id)
        return result

    _columns = {'dom_department_id': fields.function(_get_dom_department_id,
                                                     relation='hr.department',
                                                     type='many2one',
                                                     string="Dipartimento",
                                                     store=False),
                'dom_date': fields.function(_get_dom_date,
                                            type='date',
                                            string="Data Calcolo Scaduto",
                                            store=False),
                'fnct_unreconciled_aml_ids': fields.function(_get_unreconciled_aml_ids,
                                                             method=True,
                                                             type='one2many',
                                                             relation='account.move.line',
                                                             string="Righe di Sollecito"
                                                             ),
                'payment_amount_due': fields.function(_get_amounts_and_date,
                                                      type='float', string="Amount Due",
                                                      store=False, multi="followup",
                                                      fnct_search=_payment_due_search),
                'payment_amount_overdue': fields.function(_get_amounts_and_date,
                                                          type='float', string="Amount Overdue",
                                                          store=False, multi="followup",
                                                          fnct_search=_payment_overdue_search),
                'payment_earliest_due_date': fields.function(_get_amounts_and_date,
                                                             type='date',
                                                             string="Worst Due Date",
                                                             multi="followup",
                                                             fnct_search=_payment_earliest_date_search),

                'invoiced_schema_ids': fields.one2many('accreditation.invoiced.schema', 'customer_id', 'Fatturato per Schema', copy=False),
                'small_lab_ids': fields.one2many('accreditation.small.lab', 'customer_id', 'Piccolo laboratorio', copy=False),
                }

    def _get_subaccounts(self, cr, uid, ids, vals, t_customer_flag, account_receivable_ids, t_partner_name, t_supplier_flag, account_payable_ids):
        account_receivable_id = None
        account_payable_id = None
        account_obj = self.pool.get('account.account')
        res_users_obj = self.pool.get('res.users')
        my_company = res_users_obj.browse(cr, uid, uid).company_id

        if (my_company.subaccount_auto_generation_customer and t_customer_flag and not account_receivable_ids):
            parent_account_receivable_id = my_company.account_parent_customer.id
            account_type_receivable_id = self._get_type_receivable_id(cr, uid)
            account_receivable_code = account_obj.get_max_code(cr, uid, [], parent_account_receivable_id)
            account_receivable_dict = {
                'name': t_partner_name,
                'code': account_receivable_code,
                'parent_id': parent_account_receivable_id,
                'type': 'receivable',
                'user_type': account_type_receivable_id,
                'reconcile': True}
            account_receivable_id = account_obj.create(cr, uid, account_receivable_dict)
            vals["property_account_receivable"] = account_receivable_id

        if (my_company.subaccount_auto_generation_supplier and t_supplier_flag and not account_payable_ids):
            parent_account_payable_id = my_company.account_parent_supplier.id
            account_type_payable_id = self._get_type_payable_id(cr, uid)
            account_payable_code = account_obj.get_max_code(cr, uid, [], parent_account_payable_id)
            account_payable_dict = {
                'name': t_partner_name,
                'code': account_payable_code,
                'parent_id': parent_account_payable_id,
                'type': 'payable',
                'user_type': account_type_payable_id,
                'reconcile': True}
            account_payable_id = account_obj.create(cr, uid, account_payable_dict)
            vals["property_account_payable"] = account_payable_id

        return vals, account_receivable_id, account_payable_id
