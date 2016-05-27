## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            .overflow_ellipsis {
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }z

            ${css}

.style-r2 {
    background-color: #efefef;
}
        </style>
    </head>
    <body>

        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

		<%setLang(user.lang)%>

        <!-- <div class="account_title bg" style="width: 1080px; margin-top: 20px; font-size: 12px;">Corrispettivi</div> -->

            <div class="act_as_table list_table" style="margin-top: 10px;">

                <div class="act_as_thead">
                    <div class="act_as_row labels">
                        <div class="act_as_cell first_column" style="width: 70px;">Protocollo</div>
                        <div class="act_as_cell" style="width: 70px;">Data registrazione</div>
                        <div class="act_as_cell" style="width: 200px;">Sezionale</div>
                        <div class="act_as_cell amount" style="width: 80px;">Importo totale</div>
                        <div class="act_as_cell" style="width: 30px;"></div>
                        <div class="act_as_cell" style="width: 70px;">Imposta</div>
                        <div class="act_as_cell amount" style="width: 80px;">Importo</div>
                    </div>
                </div>

                <div class="act_as_tbody">

                    <% counter = 0 %>
                    %for object in get_moves() :
                        <% counter += 1 %>
                        % if counter and (counter % 2) == 0:
                          <% style = "style-r2" %>
                        % else:
                          <% style = "" %>
                        % endif
                        %for line in tax_lines(object) :
                            %if line['index']==0:
                              <div class="act_as_row lines">
                                  <div class="act_as_cell ${style} first_column">${compute_protocol_number(object.protocol_number)}</div>
                                  <div class="act_as_cell ${style}">${ formatLang(object.date,date=True) or ''| entity}</div>
                                  <div class="act_as_cell ${style}">${object.journal_id.name or ''| entity}</div>
                                  <div class="act_as_cell ${style} amount">${ formatLang(invoice_total(object)) | entity}</div>
                                  <div class="act_as_cell ${style}"></div>
                                  <div class="act_as_cell ${style}">${ (line['tax_code'])  or ''| entity}</div>
                                  <div class="act_as_cell ${style} amount" style="padding-right: 1px;">${ formatLang(line['amount'])| entity}</div>
                              </div>
                            %else:
                              <div class="act_as_row lines">
                                  <div class="act_as_cell ${style} first_column"></div>
                                  <div class="act_as_cell ${style}"></div>
                                  <div class="act_as_cell ${style}"></div>
                                  <div class="act_as_cell ${style} amount"></div>
                                  <div class="act_as_cell ${style}"></div>
                                  <div class="act_as_cell ${style}">${ (line['tax_code'])  or ''| entity}</div>
                                  <div class="act_as_cell ${style} amount" style="padding-right: 1px;">${ formatLang(line['amount'])| entity}</div>
                              </div>
                            %endif
                        %endfor
                    %endfor

                    </div>
                </div>

    <div style="page-break-inside: avoid;">

        <div class="account_title bg" style="width: 1080px; margin-top: 20px; font-size: 12px;">Periodo di stampa dal ${formatLang(start_date(),date=True)| entity} al ${formatLang(end_date(),date=True)| entity}</div>
        <table width="100%" cellpadding="4" cellspacing="0">
        <% tax_code_list = tax_codes() %>
        <% tax_code_totals_list = tax_codes_totals() %>
            <tr>
              <td valign="top">

        <div class="account_title bg" style="width: 540px; margin-top: 20px; font-size: 12px;">Dettaglio</div>
            <div class="act_as_table list_table" style="margin-top: 10px;width: 540px;">
                <div class="act_as_thead">
                    <div class="act_as_row labels">
                        <div class="act_as_cell first_column" style="width: 70px;">Codice</div>
                        <div class="act_as_cell" style="width: 90px;">Descrizione</div>
                        <div class="act_as_cell amount" style="width: 80px;">Importo</div>
                    </div>
                </div>
                <div class="act_as_tbody">
                        %for tax_code_tuple in tax_code_list :

                              <div class="act_as_row lines">
                                  <div class="act_as_cell first_column">${tax_code_tuple[2]|entity}</div>
                                  <div class="act_as_cell">${tax_code_tuple[0]|entity}</div>
                                  <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(tax_code_tuple[1])|entity}</div>
                              </div>
                        %endfor
                    </div>
                </div>
              </td>
              <td valign="top">
        <div class="account_title bg" style="width: 540px; margin-top: 20px; font-size: 12px;">Totali</div>
            <div class="act_as_table list_table" style="margin-top: 10px;width: 540px;">

                <div class="act_as_thead">
                    <div class="act_as_row labels">
                        <div class="act_as_cell first_column" style="width: 70px;">Codice</div>
                        <div class="act_as_cell" style="width: 90px;">Descrizione</div>
                        <div class="act_as_cell amount" style="width: 80px;">Importo</div>
                    </div>
                </div>
                <div class="act_as_tbody">
                        %for tax_code_tuple in tax_code_totals_list :

                              <div class="act_as_row lines">
                                  <div class="act_as_cell first_column">${tax_code_tuple[2]|entity}</div>
                                  <div class="act_as_cell">${tax_code_tuple[0]|entity}</div>
                                  <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(tax_code_tuple[1])|entity}</div>
                              </div>
                        %endfor
                    </div>
                </div>
              </td>
            </tr>
        </table>

        <div class="account_title bg" style="width: 1080px; margin-top: 20px; font-size: 12px;">Periodo di stampa dal ${formatLang(all_start_date(),date=True)| entity} al ${formatLang(end_date(),date=True)| entity}</div>
        <table width="100%" cellpadding="4" cellspacing="0">
        <% tax_code_list = all_tax_codes() %>
        <% tax_code_totals_list = all_tax_codes_totals() %>
            <tr>
              <td valign="top">
        <div class="account_title bg" style="width: 540px; margin-top: 20px; font-size: 12px;">Dettaglio imponibili</div>
            <div class="act_as_table list_table" style="margin-top: 10px;width: 540px;">
                <div class="act_as_thead">
                    <div class="act_as_row labels">
                        <div class="act_as_cell first_column" style="width: 70px;">Codice</div>
                        <div class="act_as_cell" style="width: 90px;">Descrizione</div>
                        <div class="act_as_cell amount" style="width: 80px;">Importo</div>
                    </div>
                </div>
                <div class="act_as_tbody">
                        %for tax_code_tuple in tax_code_list :

                              <div class="act_as_row lines">
                                  <div class="act_as_cell first_column">${tax_code_tuple[2]|entity}</div>
                                  <div class="act_as_cell">${tax_code_tuple[0]|entity}</div>
                                  <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(tax_code_tuple[1])|entity}</div>
                              </div>
                        %endfor
                    </div>
                </div>
              </td>
              <td valign="top">
        <div class="account_title bg" style="width: 540px; margin-top: 20px; font-size: 12px;">Totali imponibili</div>
            <div class="act_as_table list_table" style="margin-top: 10px;width: 540px;">
                <div class="act_as_thead">
                    <div class="act_as_row labels">
                        <div class="act_as_cell first_column" style="width: 70px;">Codice</div>
                        <div class="act_as_cell" style="width: 90px;">Descrizione</div>
                        <div class="act_as_cell amount" style="width: 80px;">Importo</div>
                    </div>
                </div>
                <div class="act_as_tbody">
                        %for tax_code_tuple in tax_code_totals_list :

                              <div class="act_as_row lines">
                                  <div class="act_as_cell first_column">${tax_code_tuple[2]|entity}</div>
                                  <div class="act_as_cell">${tax_code_tuple[0]|entity}</div>
                                  <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(tax_code_tuple[1])|entity}</div>
                              </div>
                        %endfor
                    </div>
                </div>

              </td>
            </tr>
        </table>
    </div>
</body>
</html>
