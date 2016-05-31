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

        %if amount_currency(data):
        <div class="act_as_table data_table" style="width: 1205px;">
        %else:
        <div class="act_as_table data_table" style="width: 1100px;">
        %endif
            <div class="act_as_row labels" style="font-size: x-small;">
                <div class="act_as_cell" style="font-size: x-small;">${_('Chart of Account')}</div>
                <div class="act_as_cell" style="font-size: x-small;">${_('Fiscal Year')}</div>
                <div class="act_as_cell" style="font-size: x-small;">
                    %if filter_form(data) == 'filter_date':
                        ${_('Dates Filter')}
                    %else:
                        ${_('Periods Filter')}
                    %endif
                </div>
                <div class="act_as_cell" style="font-size: x-small;">${_('Accounts Filter')}</div>
                <div class="act_as_cell" style="font-size: x-small;">${_('Target Moves')}</div>
                <div class="act_as_cell" style="font-size: x-small;">${_('Initial Balance')}</div>
            </div>
            <div class="act_as_row" style="font-size: x-small;">
                <div class="act_as_cell" style="font-size: x-small;">${ chart_account.name }</div>
                <div class="act_as_cell" style="font-size: x-small;">${ fiscalyear.name if fiscalyear else '-' }</div>
                <div class="act_as_cell" style="font-size: x-small;">
                    ${_('From:')}
                    %if filter_form(data) == 'filter_date':
                        ${formatLang(start_date, date=True) if start_date else u'' }
                    %else:
                        ${start_period.name if start_period else u''}
                    %endif
                    ${_('To:')}
                    %if filter_form(data) == 'filter_date':
                        ${ formatLang(stop_date, date=True) if stop_date else u'' }
                    %else:
                        ${stop_period.name if stop_period else u'' }
                    %endif
                </div>
                <div class="act_as_cell" style="font-size: x-small;">
                    %if accounts(data):
                        ${', '.join([account.code for account in accounts(data)])}
                    %else:
                        ${_('All')}
                    %endif

                </div>
                <div class="act_as_cell" style="font-size: x-small;">${ display_target_move(data) }</div>
                <div class="act_as_cell" style="font-size: x-small;">${ initial_balance_text[initial_balance_mode] }</div>
            </div>
        </div>

        <!-- we use div with css instead of table for tabular data because div do not cut rows at half at page breaks -->
        %for account in objects:
        <%
          display_initial_balance = init_balance[account.id] and (init_balance[account.id].get('debit') != 0.0 or init_balance[account.id].get('credit', 0.0) != 0.0)
          display_ledger_lines = ledger_lines[account.id]
        %>
          %if display_account_raw(data) == 'all' or (display_ledger_lines or display_initial_balance):
              <%
              cumul_debit = 0.0
              cumul_credit = 0.0
              cumul_balance =  0.0
              cumul_balance_curr = 0.0
              %>
            <div class="act_as_table list_table" style="margin-top: 10px; font-size: x-small;">

                <div class="act_as_caption account_title" style="font-size: x-small;">
                    ${account.code} - ${account.name}
                </div>
                <div class="act_as_thead" style="font-size: x-small;">
                    <div class="act_as_row labels" style="font-size: x-small;">
                        ## date
                        <div class="act_as_cell first_column" style="width: 65px; font-size: x-small;">${_('Date')}</div>
                        ## period
                        <div class="act_as_cell" style="width: 60px; font-size: x-small;">${_('Period')}</div>
                        ## move
                        <div class="act_as_cell" style="width: 100px; font-size: x-small;">${_('Entry')}</div>
                        ## partner
                        <div class="act_as_cell" style="width: 156px; font-size: x-small;">${_('Partner')}</div>
						## move reference
                        <div class="act_as_cell" style="width: 156px;">${_('Reference')}</div>           
                        ## date document             
                        <div class="act_as_cell" style="width: 65px; font-size: x-small;">${_('Data Doc.')}</div>
                        ## label
                        <div class="act_as_cell" style="width: 170px; font-size: x-small;">${_('Label')}</div>

                        ## debit
                        <div class="act_as_cell amount" style="width: 76px; font-size: x-small;">${_('Dare')}</div>
                        ## credit
                        <div class="act_as_cell amount" style="width: 76px; font-size: x-small;">${_('Avere')}</div>
                        ## balance cumulated
                        <div class="act_as_cell amount" style="width: 76px; font-size: x-small;">${_('Cumul. Bal.')}</div>
                        %if amount_currency(data):
                            ## currency balance
                            <div class="act_as_cell amount sep_left" style="width: 75px; font-size: x-small;">${_('Curr. Balance')}</div>
                            ## curency code
                            <div class="act_as_cell amount" style="width: 30px; text-align: right; font-size: x-small;">${_('Curr.')}</div>
                        %endif
                    </div>
                </div>

                <div class="act_as_tbody" style="font-size: x-small; page-break-inside:avoid; ">
                      %if display_initial_balance:
                        <%
                        cumul_debit = init_balance[account.id].get('debit') or 0.0
                        cumul_credit = init_balance[account.id].get('credit') or 0.0
                        cumul_balance = init_balance[account.id].get('init_balance') or 0.0
                        cumul_balance_curr = init_balance[account.id].get('init_balance_currency') or 0.0
                        %>
                        <div class="act_as_row initial_balance" style="page-break-inside:avoid; font-size: x-small; page-break-inside:avoid; ">
                          ## date
                          <div class="act_as_cell first_column" style="font-size: x-small;"></div>
                          ## period
                          <div class="act_as_cell" style="font-size: x-small;"></div>
                          ## move
                          <div class="act_as_cell" style="font-size: x-small;"></div>
                          ## partner
                          <div class="act_as_cell" style="font-size: x-small;"></div>
                          ## move reference
                          <div class="act_as_cell"></div>                          
                          ##Data Doc.
                          <div class="act_as_cell" style="font-size: x-small;"></div>
                          ## label
                          <div class="act_as_cell" style="font-size: x-small;">${_('Initial Balance')}</div>
                          ## debit
                          <div class="act_as_cell amount" style="font-size: x-small;">${formatLang(init_balance[account.id].get('debit')) | amount}</div>
                          ## credit
                          <div class="act_as_cell amount" style="font-size: x-small;">${formatLang(init_balance[account.id].get('credit')) | amount}</div>
                          ## balance cumulated
                          <div class="act_as_cell amount" style="padding-right: 1px; font-size: x-small;">${formatLang(cumul_balance) | amount }</div>
                         %if amount_currency(data):
                              ## currency balance
                              <div class="act_as_cell amount sep_left" style="font-size: x-small;">${formatLang(cumul_balance_curr) | amount }</div>
                              ## curency code
                              <div class="act_as_cell amount" style="font-size: x-small;"></div>
                         %endif

                        </div>
                      %endif
                      %for line in ledger_lines[account.id]:
                        <%
                        cumul_debit += line.get('debit') or 0.0
                        cumul_credit += line.get('credit') or 0.0
                        cumul_balance_curr += line.get('amount_currency') or 0.0
                        cumul_balance += line.get('balance') or 0.0
                        label_elements = [line.get('lname') or '']
                        if line.get('invoice_number'):
                          label_elements.append("(%s)" % (line['invoice_number'],))
                        label = ' '.join(label_elements)
                        %>

                      <div class="act_as_row lines" style="page-break-inside:avoid; font-size: x-small; page-break-inside:avoid; ">
                          ## date
                          <div class="act_as_cell first_column" style="font-size: x-small;">${formatLang(line.get('ldate') or '', date=True)}</div>
                          ## period
                          <div class="act_as_cell" style="font-size: x-small;">${line.get('period_code') or ''}</div>
                          ## move
                          <div class="act_as_cell" style="font-size: x-small;">${line.get('move_name') or ''}</div>
                          ## partner
                          <div class="act_as_cell overflow_ellipsis" style="font-size: x-small;">${line.get('partner_name') or ''}</div>
                          ## move reference
                          <div class="act_as_cell">${line.get('lref') or ''}</div>                          
                          ## Data Doc.
                          <div class="act_as_cell" style="font-size: x-small;">${formatLang(line.get('document_date') or '', date=True)}</div>
                          ## label
                          <div class="act_as_cell overflow_ellipsis" style="font-size: x-small;">${label}</div>
                          ## debit
                          <div class="act_as_cell amount" style="font-size: x-small;">${ line.get('debit', 0.0) | amount }</div>
                          ## credit
                          <div class="act_as_cell amount" style="font-size: x-small;">${ line.get('credit', 0.0) | amount }</div>
                          ## balance cumulated
                          <div class="act_as_cell amount" style="padding-right: 1px;" font-size: x-small;>${ formatLang(cumul_balance) | amount }</div>
                          %if amount_currency(data):
                              ## currency balance
                              <div class="act_as_cell amount sep_left" style="font-size: x-small;">${formatLang(line.get('amount_currency') or 0.0)  | amount }</div>
                              ## curency code
                              <div class="act_as_cell amount" style="text-align: right; font-size: x-small;">${line.get('currency_code') or ''}</div>
                          %endif
                      </div>
                      %endfor
                </div>
                <div class="act_as_table list_table" style="font-size: x-small; page-break-inside:avoid; ">
                    <div class="act_as_row labels" style="page-break-inside:avoid; font-weight: bold; font-size: x-small; page-break-inside:avoid; ">
                        ## date
                        <div class="act_as_cell first_column" style="width: 602px; font-size: x-small;">${account.code} - ${account.name}</div>
                        <div class="act_as_cell" style="width: 170px; font-size: x-small;">${_("Cumulated Balance on Account")}</div>
                        ## debit
                        <div class="act_as_cell amount" style="width: 76px; text-align: right; font-size: x-small;">${ formatLang(cumul_debit) | amount }</div>
                        ## credit
                        <div class="act_as_cell amount" style="width: 76px; text-align: right; font-size: x-small;">${ formatLang(cumul_credit) | amount }</div>
                        ## balance cumulated
                        <div class="act_as_cell amount" style="width: 76px; text-align: right; font-size: x-small; padding-right: 1px;">${ formatLang(cumul_balance) | amount }</div>
                        %if amount_currency(data):
                            %if account.currency_id:
                                ## currency balance
                                <div class="act_as_cell amount sep_left" style="width: 75px; text-align: right; font-size: x-small;">${formatLang(cumul_balance_curr) | amount }</div>
                            %else:
                                <div class="act_as_cell amount sep_left" style="width: 75px; text-align: right; font-size: x-small;">-</div>
                            %endif
                            ## curency code
                            <div class="act_as_cell amount" style="width: 30px; text-align: right; font-size: x-small;"></div>
                        %endif
                    </div>
                </div>
            </div>
          %endif
        %endfor
    </body>
</html>
