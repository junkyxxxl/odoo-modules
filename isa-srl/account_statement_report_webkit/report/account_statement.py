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

import os
from datetime import datetime

from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class AccountReportStatement(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):

    def __init__(self, cursor, uid, name, context):
        super(AccountReportStatement, self).__init__(cursor, uid, name, context=context)
        self.cursor = self.cr
        self.date_start = None
        self.filter = None

        self.company = self.pool.get('wizard.account.statement').browse(self.cr, self.uid, context['active_id']).company_id        
        header_report_name = ' - '.join((_('Estratto Conto Per Partita'), self.company.name, self.company.currency_id.name))

        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)

        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'get_accounts':self._get_accounts,
            'get_moves':self._get_moves,
            'get_move_lines':self._get_move_lines,
            'get_date_start': self._get_date_start,
            'get_filter': self._get_filter,
            'display_target_move': self._get_display_target_move,
            'report_name': _('Estratto Conto Per Partita'),
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_date_start(self, form_values):

        if form_values['date_from']:
            self.date_start = form_values['date_from']

        return self.date_start

    def _get_filter(self, form_values):
        t_dict = {}
        if form_values['statement_type']:
            self.filter = form_values['statement_type']
            t_dict = dict([('O', 'Aperte'), ('H', 'Chiuse'), ('E', 'Aperte e Chiuse')])

        return t_dict[self.filter]

    def _get_accounts(self, form_values):
        selected_items = form_values['account_ids']
        if not selected_items:
            return []
        t_items = "(" + str(selected_items) + ")"
        if isinstance(selected_items, list):
            t_items = "(" + ",".join(str(x) for x in selected_items) + ") "

        query = """
                      select account_account.id,
                             account_account.code as account_code,
                             account_account.name as account_name
                      from account_account
                      WHERE account_account.id IN """ + t_items + """
                      AND company_id = """ + str(self.company.id) + """
                      order by account_name
                      """

        self.cr.execute(query)
        res = self.cr.dictfetchall()

        return res

    def _get_open_move(self, form_values, account):
        t_items = "(" + str(account) + ")"

        query_move = """
                   select account_move.id, account_move.name AS move_name
                   from account_move
                   where account_move.id in 
                      (
                      select account_move.id
                      from account_move
                          join account_move_line
                              on account_move_line.move_id = account_move.id
                          join account_account
                              on account_move_line.account_id = account_account.id
                          LEFT JOIN account_invoice 
                              on (account_move.id = account_invoice.move_id)
                      WHERE account_account.id IN """ + t_items + """
                            and account_move_line.unsolved_move_originator_id is null
                            and account_move_line.intra_move_originator_id is null
                            and account_invoice.id is not null
                        ) AND
                    account_move.company_id = """ + str(self.company.id) + """ """

        if form_values['date_from']:
            query_move += "AND (account_move.date>='" + form_values['date_from'] + "') "

        if form_values['target_move'] and form_values['target_move'] == 'posted':
            query_move +=  """ AND (account_move.state like 'posted') """

        query_move += """ and account_move.id not in (
                             select account_move.id
                             from account_move
                             where account_move.id in ( 

                                  select account_move.id
                                  from account_move
                                  join account_move_line
                                      on account_move_line.move_id = account_move.id
                                  join account_account
                                      on account_move_line.account_id = account_account.id
                                                  LEFT JOIN account_invoice on (account_move.id = account_invoice.move_id)
                                  WHERE account_account.id IN """ + t_items + " "

        if form_values['date_from']:
            query_move += "AND (account_move.date>='" + form_values['date_from'] + "') "

        if form_values['target_move'] and form_values['target_move'] == 'posted':
            query_move += "AND (account_move.state like 'posted') "

        query_move += """
                                  and account_invoice.id is not null 
                          except
                
                                  select account_move.id
                                  from account_move
                                  join account_move_line
                                      on account_move_line.move_id = account_move.id
                                  join account_account
                                      on account_move_line.account_id = account_account.id
                                  WHERE account_account.id IN """ + t_items + " "

        if form_values['date_from']:
            query_move += "AND (account_move.date>='" + form_values['date_from'] + "') "

        if form_values['target_move'] and form_values['target_move'] == 'posted':
            query_move += "AND (account_move.state like 'posted') "

        query_move += """
                                  and account_move_line.reconcile_id is null
                      except
            
                              select account_move.id
                              from account_move
                              join account_move_line
                                  on account_move_line.intra_move_originator_id = account_move.id
                              join account_account
                                  on account_move_line.account_id = account_account.id
                              WHERE account_account.id IN """ + t_items + " "

        query_move += """
                                  and account_move_line.reconcile_id is null 
                              group by account_move.id
                      except
            
                              select account_move.id
                              from account_move
                              join account_move_line
                                  on account_move_line.auto_move_originator_id = account_move.id
                              join account_account
                                  on account_move_line.account_id = account_account.id
                              WHERE account_account.id IN """ + t_items + " "

        query_move += """
                                  and account_move_line.reconcile_id is null 
                              group by account_move.id

                                   ) """

        query_move += """ )
                      order by account_move.name
                        """
        return query_move

    def _get_closed_move(self, form_values, account):
        t_items = "(" + str(account) + ")"

        query_move = """
                        select account_move.id
                        from account_move
                        where account_move.id in (
                              select account_move.id
                              from account_move
                              join account_move_line
                                  on account_move_line.move_id = account_move.id
                              join account_account
                                  on account_move_line.account_id = account_account.id
                              LEFT JOIN account_invoice on (account_move.id = account_invoice.move_id)
                              WHERE account_account.id IN """ + t_items + """
                                    and account_move_line.unsolved_move_originator_id is null
                                    and account_move_line.intra_move_originator_id is null
                        AND account_move.company_id = """ + str(self.company.id) + """ """

        if form_values['date_from']:
            query_move += "AND (account_move.date>='" + form_values['date_from'] + "') "

        if form_values['target_move'] and form_values['target_move'] == 'posted':
            query_move += "AND (account_move.state like 'posted') "

        query_move += """
                                  and account_invoice.id is not null 
                              group by account_move.id
            
                      except
            
                              select account_move.id
                              from account_move
                              join account_move_line
                                  on account_move_line.move_id = account_move.id
                              join account_account
                                  on account_move_line.account_id = account_account.id
                              WHERE account_account.id IN """ + t_items + " "

        if form_values['date_from']:
            query_move += "AND (account_move.date>='" + form_values['date_from'] + "') "

        if form_values['target_move'] and form_values['target_move'] == 'posted':
            query_move += "AND (account_move.state like 'posted') "

        query_move += """
                                  and account_move_line.reconcile_id is null 
                              group by account_move.id
                      except
            
                              select account_move.id
                              from account_move
                              join account_move_line
                                  on account_move_line.intra_move_originator_id = account_move.id
                              join account_account
                                  on account_move_line.account_id = account_account.id
                              WHERE account_account.id IN """ + t_items + " "

        query_move += """
                                  and account_move_line.reconcile_id is null 
                              group by account_move.id
                      except
            
                              select account_move.id
                              from account_move
                              join account_move_line
                                  on account_move_line.auto_move_originator_id = account_move.id
                              join account_account
                                  on account_move_line.account_id = account_account.id
                              WHERE account_account.id IN """ + t_items + " "

        query_move += """
                                  and account_move_line.reconcile_id is null 
                              group by account_move.id
                        )
                        order by account_move.name

        """

        return query_move

    def _get_all_move(self, form_values, account):
        t_items = "(" + str(account) + ")"

        query_move = """
                      select account_move.id, account_move.name AS move_name
                      from account_move
                          join account_move_line
                              on account_move_line.move_id = account_move.id
                          join account_account
                              on account_move_line.account_id = account_account.id
                      WHERE account_account.id IN """ + t_items + """
                            and account_move_line.unsolved_move_originator_id is null
                            and account_move_line.intra_move_originator_id is null
                            AND account_move.company_id = """ + str(self.company.id) + """ """

        if form_values['date_from']:
            query_move += "AND (account_move.date>='" + form_values['date_from'] + "') "

        if form_values['target_move'] and form_values['target_move'] == 'posted':
            query_move += "AND (account_move.state like 'posted') "

        query_move += """
                      group by account_move.id
                      order by account_move.name
        """

        return query_move

    def _get_moves(self, form_values, account):
        query_str = ''
        if form_values['statement_type'] == 'O':
            query_str = self._get_open_move(form_values, account)
        elif form_values['statement_type'] == 'H':
            query_str = self._get_closed_move(form_values, account)

        else:
            query_str = self._get_all_move(form_values, account)

        self.cr.execute(query_str)
        res = self.cr.dictfetchall()

        return res

    def _get_move_lines(self, move_id, account_id, form_values = None):

        query_move_lines = """
                SELECT l.id AS id,
                            m.date AS ldate,
                            j.code AS jcode ,
                            l.currency_id,
                            a.id AS account_id,
                            a.code AS account_code,
                            a.name AS account_name,
                            l.amount_currency,
                            l.ref AS lref,
                            m.document_date as document_date,
                            l.name AS lname,
                            COALESCE(l.debit, 0.0) - COALESCE(l.credit, 0.0) AS balance,
                            l.debit,
                            l.credit,
                            l.period_id AS lperiod_id,
                            l.unsolved_move_originator_id AS unsolved_move_originator,
                            l.intra_move_originator_id AS intra_move_originator,
                            per.code as period_code,
                            per.special AS peropen,
                            l.partner_id AS lpartner_id,
                            p.name AS partner_name,
                            m.name AS move_name,
                            COALESCE(partialrec.name, fullrec.name, '') AS rec_name,
                            m.id AS move_id,
                            c.name AS currency_code,
                            i.id AS invoice_id,
                            i.type AS invoice_type,
                            i.number AS invoice_number,
                            l.date_maturity AS date_maturity
                FROM account_move_line l
                    JOIN account_move m on (l.move_id=m.id)
                    JOIN account_account a on (l.account_id = a.id)
                    LEFT JOIN res_currency c on (l.currency_id=c.id)
                    LEFT JOIN account_move_reconcile partialrec on (l.reconcile_partial_id = partialrec.id)
                    LEFT JOIN account_move_reconcile fullrec on (l.reconcile_id = fullrec.id)
                    LEFT JOIN res_partner p on (l.partner_id=p.id)
                    LEFT JOIN account_invoice i on (m.id =i.move_id)
                    LEFT JOIN account_period per on (per.id=l.period_id)
                    JOIN account_journal j on (l.journal_id=j.id)

                WHERE l.id in
                   (
                           select account_move_line.id
                           from account_move_line
                                  join account_move
                                      on account_move_line.move_id = account_move.id
                                  join account_account
                                      on account_move_line.account_id = account_account.id
                           where account_move_line.move_id = """ + str(move_id) + """
                                 and account_account.id = """ + str(account_id) + """
                     union
                           select account_move_line.id
                           from account_move_line, account_move
                           where account_move_line.reconcile_id in  (    
        
                                select account_move_line.reconcile_id
                                from account_move_line
                                    join account_account
                                        on account_move_line.account_id = account_account.id
                                    join account_move
                                        on account_move_line.move_id = account_move.id
                                where account_move_line.move_id = """ + str(move_id) + """
                                and account_account.id = """ + str(account_id) + """
                                ) 
                            and account_move_line.move_id = account_move.id """ +  (form_values and form_values['target_move'] and form_values['target_move'] == 'posted' and "and account_move.state like 'posted'" or '') + """
                     union
                           select account_move_line.id
                           from account_move_line, account_account, account_move
                           where account_move_line.move_id = account_move.id and account_move_line.unsolved_move_originator_id = """ + str(move_id) + """
                           and account_account.id = """ + str(account_id) + """ and account_move_line.account_id = account_account.id
                           """ +  (form_values and form_values['target_move'] and form_values['target_move'] == 'posted' and "and account_move.state like 'posted'" or '') + """
                     union
                           select account_move_line.id
                           from account_move_line, account_account, account_move
                           where account_move_line.move_id = account_move.id and account_move_line.intra_move_originator_id = """ + str(move_id) + """
                           and account_account.id = """ + str(account_id) + """ and account_move_line.account_id = account_account.id
                           """ +  (form_values and form_values['target_move'] and form_values['target_move'] == 'posted' and "and account_move.state like 'posted'" or '') + """                           
                     union
                           select account_move_line.id
                           from account_move_line, account_move
                           where account_move_line.move_id = account_move.id and account_move_line.reconcile_id in  (    
        
                           select account_move_line.reconcile_id
                           from account_move_line, account_account
                           where account_move_line.unsolved_move_originator_id = """ + str(move_id) + """
                           and account_account.id = """ + str(account_id) + """ and account_move_line.account_id = account_account.id
                                )
                           """ +  (form_values and form_values['target_move'] and form_values['target_move'] == 'posted' and "and account_move.state like 'posted'" or '') + """                                                              
                     union
                           select account_move_line.id
                           from account_move_line, account_move
                           where account_move_line.move_id = account_move.id and account_move_line.reconcile_partial_id in  ( 
                               select account_move_line.reconcile_partial_id
                               from account_move_line, account_account, account_move
                               where account_move_line.unsolved_move_originator_id = """ + str(move_id) + """
                               and account_account.id = """ + str(account_id) + """ 
                               and account_move_line.account_id = account_account.id
                               and account_move_line.move_id = account_move.id
                           )               
                           """ +  (form_values and form_values['target_move'] and form_values['target_move'] == 'posted' and "and account_move.state like 'posted'" or '') + """                                                                                                                                   
                     union
                           select account_move_line.id
                           from account_move_line, account_move
                           where account_move_line.move_id = account_move.id and account_move_line.reconcile_partial_id in  ( 
                                select account_move_line.reconcile_partial_id
                                from account_move_line
                                    join account_account
                                        on account_move_line.account_id = account_account.id
                                    join account_move
                                        on account_move_line.move_id = account_move.id
                                where account_move_line.move_id = """ + str(move_id) + """
                                and account_account.id = """ + str(account_id) + """
                                )
                           """ +  (form_values and form_values['target_move'] and form_values['target_move'] == 'posted' and "and account_move.state like 'posted'" or '') + """                                                                                                                                                                   
                   )
                 order by l.move_id, l.reconcile_id, l.reconcile_partial_id
                 """

        self.cr.execute(query_move_lines)
        res = self.cr.dictfetchall()

        return res

HeaderFooterTextWebKitParser('report.account.report.statement',
                             'account.account',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                         '/templates/account_report_statement.mako',
                             parser=AccountReportStatement)
