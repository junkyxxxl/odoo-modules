## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            .overflow_ellipsis {
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }

            ${css}
        </style>
    </head>
    <body>

        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

		<%setLang(user.lang)%>

        <%
        initial_balance_text = {'initial_balance': _('Computed'), 'opening_balance': _('Opening Entries'), False: _('No')}
        %>
        <%
            t_filter = get_filter(data['form'])
        %>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell">${_('Filtro Data')}</div>
                <div class="act_as_cell">${_('Filtro Partite')}</div>
                <div class="act_as_cell">${_('Registrazioni')}</div>
                <div class="act_as_cell"></div>
                <div class="act_as_cell"></div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${_('Da:')} ${formatLang(get_date_start(data['form']) or '', date=True)}</div>
                <div class="act_as_cell">${t_filter or ''}</div>
                <div class="act_as_cell">${ display_target_move(data) }</div>
                <div class="act_as_cell"><br></div>
                <div class="act_as_cell"><br></div>
            </div>
        </div>


        %for account in get_accounts(data['form']):
            <%
                temp_account_debit = 0.0
                temp_account_credit = 0.0
                temp_account_balance = 0.0

                temp_move_blacklist = []
                flag_account_header = True
            %>

            %for move in get_moves(data['form'],account['id']):

                %if flag_account_header:
                    <div class="account_title bg" style="width: 1080px; margin-top: 20px; font-size: 12px;">${account.get('account_code') or ''} - ${account.get('account_name') or ''}</div>
                    <%
                        flag_account_header = False
                    %>
                %endif

                %if move['id'] not in temp_move_blacklist:

                    <%
                        cumul_balance = 0.0
        
                        temp_debit = 0.0
                        temp_credit = 0.0
                        temp_balance = 0.0
                    %>
    
                    <div class="act_as_table list_table" style="margin-top: 10px;">
                        
                        <div class="act_as_caption account_title">
                            ${move.get('move_name') or ''}
                        </div>
        
                        <div class="act_as_thead" style='page-break-inside:avoid;'>
                            <div class="act_as_row labels" style='page-break-inside:avoid;'>
                                <div class="act_as_cell first_column" style="width: 50px;">Data</div>
                                <div class="act_as_cell" style="width: 60px;">Periodo</div>
                                <div class="act_as_cell" style="width: 80px;">Voce</div>
                                <div class="act_as_cell" style="width: 70px;">Sezionale</div>
                                <div class="act_as_cell" style="width: 60px;">Partner</div>
                                <div class="act_as_cell" style="width: 220px;">Etichetta</div>
                                <div class="act_as_cell" style="width: 80px;">Num. Doc. Origine</div>
                                <div class="act_as_cell" style="width: 50px;">Data Doc.</div>
                                <div class="act_as_cell" style="width: 50px;">Scadenza</div>
                                <div class="act_as_cell" style="width: 50px;">Riconc.</div>
                                <div class="act_as_cell amount" style="width: 50px;">Dare</div>
                                <div class="act_as_cell amount" style="width: 50px;">Avere</div>
                                <div class="act_as_cell amount" style="width: 80px;">Saldo Progr.</div>
                            </div>
                        </div>

                        <div class="act_as_tbody">

                        %for line in get_move_lines(move['id'],account['id'],data['form'],):
                            <%
                                if line.get('rec_name'):
                                    temp_move_blacklist.append(line['move_id'])

                                if line.get('intra_move_originator'):
                                    temp_move_blacklist.append(line['intra_move_originator'])

                                if line.get('unsolved_move_originator'):
                                    temp_move_blacklist.append(line['unsolved_move_originator'])

                                label_elements = [line.get('lname') or '']
                                if line.get('invoice_number'):
                                    label_elements.append("(%s)" % (line['invoice_number'],))
                                label = ' '.join(label_elements)
                            %>
                            <div class="act_as_row lines" style='page-break-inside:avoid;'>
                                <div class="act_as_cell first_column">${formatLang(line.get('ldate') or '', date=True)}</div>
                                <div class="act_as_cell">${line.get('period_code') or ''}</div>
                                <div class="act_as_cell">${line.get('move_name') or ''}</div>
                                <div class="act_as_cell">${line.get('jcode') or ''}</div>
                                <div class="act_as_cell overflow_ellipsis">${line.get('partner_name') or ''}</div>
                                <div class="act_as_cell">${label}</div>
                                <div class="act_as_cell">${line.get('lref') or ''}</div>
                                <div class="act_as_cell">${formatLang(line.get('document_date') or '', date=True)}</div>
                                <div class="act_as_cell">${formatLang(line.get('date_maturity') or '', date=True)}</div>
                                <div class="act_as_cell">${line.get('rec_name') or ''}</div>
                                <div class="act_as_cell amount">${formatLang(line.get('debit') or 0.0) | amount }</div>
                                <div class="act_as_cell amount">${formatLang(line.get('credit') or 0.0) | amount }</div>
                                <% cumul_balance += line.get('balance') %>
                                <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(cumul_balance) | amount }</div>
                            </div>
    
                            <%
                                temp_debit += line.get('debit')
                                temp_credit += line.get('credit')
                                temp_balance += line.get('debit') - line.get('credit')
                                temp_account_debit += line.get('debit')
                                temp_account_credit += line.get('credit')
                                temp_account_balance += line.get('debit') - line.get('credit')
                            %>
                        %endfor
    
                        <div class="act_as_row lines labels" style='page-break-inside:avoid;'>
                          <div class="act_as_cell first_column"></div>
                          <div class="act_as_cell"></div>
                          <div class="act_as_cell"></div>
                          <div class="act_as_cell"></div>
                          <div class="act_as_cell"></div>
                          <div class="act_as_cell"></div>
                          <div class="act_as_cell">Saldo Partita</div>
                          <div class="act_as_cell"></div>
                          <div class="act_as_cell"></div>
                          <div class="act_as_cell"></div>
                          <div class="act_as_cell amount">${formatLang(temp_debit) | amount }</div>
                          <div class="act_as_cell amount">${formatLang(temp_credit) | amount }</div>
                          <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(temp_balance) | amount }</div>
                      </div>
        
                    </div>
                </div>
                %endif

            %endfor

            %if not flag_account_header:
                <div class="act_as_table list_table" style="margin-top:5px;">
                    <div class="act_as_row labels" style="font-weight: bold; font-size: 9px; page-break-inside:avoid; ">
                            <div class="act_as_cell first_column" style="width: 320px;">${account.get('account_code') or ''} - ${account.get('account_name') or ''}</div>
                            <div class="act_as_cell" style="width: 450px;">Saldo Cumulativo su Conto</div>
                            <div class="act_as_cell amount" style="width: 50px;">${formatLang(temp_account_debit) | amount }</div>
                            <div class="act_as_cell amount" style="width: 50px;">${formatLang(temp_account_credit) | amount }</div>
                            <div class="act_as_cell amount" style="width: 80px; padding-right: 1px;">${formatLang(temp_account_balance) | amount }</div>
                        </div>
                    </div>
                </div>

            %endif
        %endfor

    </body>
</html>
