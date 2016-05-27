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
        <%
        flag_print_final = data["print_final"]
        fiscalyear_id = data["form"]["fiscalyear"]

        print_info = get_print_info(fiscalyear_id)
        result_rows = get_assets(print_info['year_name'])

        page_rows = 20
        
        num_rows = len(result_rows)
        num_row = 0
        new_page = True
        style = ""

        progr_page = 0
        progr_row = 0

        last_asset_category_header = 0
        last_asset_category_name = ''
        flag_asset_category_header = True
        last_asset_header = 0
        flag_asset_header = True
        prev_line = None

        tot_value = 0.0
        tot_amount = 0.0
        tot_depreciated_value = 0.0
        tot_remaining_value = 0.0

        tot_cat_value = 0.0
        tot_cat_amount = 0.0
        tot_cat_depreciated_value = 0.0
        tot_cat_remaining_value = 0.0
        tot_cat_name = ''
        %>
		<%setLang(user.lang)%>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell">${_('Anno Fiscale')}</div>
                <div class="act_as_cell"></div>
                <div class="act_as_cell"></div>
                <div class="act_as_cell"></div>
                <div class="act_as_cell"></div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${print_info['year_name']}</div>
                <div class="act_as_cell"><br></div>
                <div class="act_as_cell">
                    %if flag_print_final == False:
                        ${ _("TEST PRINTING") }
                    %endif
                </div>
                <div class="act_as_cell">
                    %if flag_print_final == False:
                        ${ _("TEST PRINTING") }
                    %endif
                </div>
                <div class="act_as_cell">
                    %if flag_print_final == False:
                        ${ _("TEST PRINTING") }
                    %endif
                </div>
            </div>
        </div>

        %for line in result_rows :
                %if last_asset_header != 0 and last_asset_header != line.get('asset_id'):
                            <div class="act_as_row lines labels">
                              <div class="act_as_cell first_column">Totale cespite</div>
                              <div class="act_as_cell"></div>
                              <div class="act_as_cell amount">${formatLang(tot_value or '') | amount }</div>
                              <div class="act_as_cell amount"></div>
                              <div class="act_as_cell amount">${formatLang(tot_depreciated_value or '') | amount }</div>
                              <div class="act_as_cell amount">${formatLang(tot_amount or '') | amount }</div>
                              <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(line.get('tot_remaining_value') or '') | amount }</div>
                            </div>
        
                        </div>
                    </div>
                    <%
                    tot_cat_value = tot_cat_value + tot_value
                    tot_cat_amount = tot_cat_amount + tot_amount
                    tot_cat_depreciated_value = tot_cat_depreciated_value + tot_depreciated_value
                    tot_cat_remaining_value = tot_cat_remaining_value + tot_remaining_value
                    tot_cat_name = line.get('category_name')
                    
                    tot_value = 0.0
                    tot_amount = 0.0
                    tot_depreciated_value = 0.0
                    tot_remaining_value = 0.0
                    %>
                %endif

                %if last_asset_category_header != 0 and last_asset_category_header != line.get('category_id'):

                    <div class="act_as_table list_table" style="margin-top:5px;">
                        <div class="act_as_row labels" style="font-weight: bold; font-size: 12px;">
                                <div class="act_as_cell first_column" style="width: 40px;">Totale</div>
                                <div class="act_as_cell" style="width: 50px;">${last_asset_category_name}</div>
                                <div class="act_as_cell amount" style="width: 40px;">${formatLang(tot_cat_value or '') | amount }</div>
                                <div class="act_as_cell" style="width: 60px;"></div>
                                <div class="act_as_cell amount" style="width: 90px;">${formatLang(tot_cat_depreciated_value or '') | amount }</div>
                                <div class="act_as_cell amount" style="width: 90px;">${formatLang(tot_cat_amount or '') | amount }</div>
                                <div class="act_as_cell amount" style="width: 90px; padding-right: 1px;"></div>
                            </div>
                        </div>
                    </div>
                    <%
                    tot_cat_value = 0.0
                    tot_cat_amount = 0.0
                    tot_cat_depreciated_value = 0.0
                    tot_cat_remaining_value = 0.0
                    %>
                %endif

                %if last_asset_category_header == 0 or last_asset_category_header != line.get('category_id'):
                    <div class="account_title bg" style="width: 1080px; margin-top: 20px; font-size: 12px;">${_('Categoria')} ${line.get('category_name') or ''}</div>
                    <%
                        last_asset_category_header = line.get('category_id')
                        last_asset_category_name   = line.get('category_name')
                        flag_asset_category_header = True
                    %>
                %endif

                %if last_asset_header == 0 or last_asset_header != line.get('asset_id'):
                    <div class="act_as_table list_table" style="margin-top: 10px;">

                        <div class="act_as_caption account_title">
                            ${_('Cespite')} ${line.get('asset_name') or ''}
                        </div>

                        <div class="act_as_thead">
                            <div class="act_as_row labels">
                                <div class="act_as_cell first_column" style="width: 40px;">${_('Data Operazione')}</div>
                                <div class="act_as_cell" style="width: 50px;">${_('Operazione')}</div>
                                <div class="act_as_cell amount" style="width: 40px;">${_('Valore iniziale')}</div>
                                <div class="act_as_cell amount" style="width: 60px;">${_('% Amm.to')}</div>
                                <div class="act_as_cell amount" style="width: 90px;">${_('Importo già ammortizzato')}</div>
                                <div class="act_as_cell amount" style="width: 90px;">${_('Ammortamento corrente')}</div>
                                <div class="act_as_cell amount" style="width: 90px;">${_('Residuo da amm.')}</div>
                            </div>
                        </div>

                        <div class="act_as_tbody">
                        <%
                            last_asset_header = line.get('asset_id')
                            flag_asset_header = True
                        %>

                        <div class="act_as_row lines">
                            <div class="act_as_cell first_column">${ formatLang(line.get('purchase_date'), date=True) or ''|entity }</div>
                            <div class="act_as_cell">${_('Acquisizione')}</div>
                            <div class="act_as_cell amount">${formatLang(line.get('purchase_value') or '') | amount }</div>
                            <div class="act_as_cell amount"></div>
                            <div class="act_as_cell amount"></div>
                            <div class="act_as_cell amount"></div>
                            <div class="act_as_cell amount" style="padding-right: 1px;"></div>
                        </div>
                %endif

                <div class="act_as_row lines">
                    <div class="act_as_cell first_column">${ formatLang(line.get('depreciation_date'), date=True) or ''|entity }</div>
                    <div class="act_as_cell">${_('Amm.to ordinario')}</div>
                    <div class="act_as_cell amount"></div>
                    <div class="act_as_cell amount">${float(line.get('amount')) / float(line.get('purchase_value')) * 100} </div>
                    <div class="act_as_cell amount">${formatLang(line.get('depreciated_value') or '') | amount }</div>
                    <div class="act_as_cell amount">${formatLang(line.get('amount') or '') | amount }</div>
                    <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(line.get('remaining_value') or '') | amount }</div>
                </div>

                <%
                prev_line = line
        
                tot_value = line.get('purchase_value')
                tot_amount = tot_amount + line.get('amount')
                tot_depreciated_value = tot_depreciated_value + line.get('depreciated_value')
                tot_remaining_value = tot_remaining_value + line.get('remaining_value')
                %>
        %endfor
    
        %if prev_line:

            <%
            tot_cat_value = tot_cat_value + tot_value
            tot_cat_amount = tot_cat_amount + tot_amount
            tot_cat_depreciated_value = tot_cat_depreciated_value + tot_depreciated_value
            tot_cat_remaining_value = tot_cat_remaining_value + tot_remaining_value
            tot_cat_name = prev_line.get('category_name')
            %>
                            <div class="act_as_row lines labels">
                              <div class="act_as_cell first_column">Totale cespite</div>
                              <div class="act_as_cell"></div>
                              <div class="act_as_cell amount">${formatLang(tot_value or '') | amount }</div>
                              <div class="act_as_cell amount"></div>
                              <div class="act_as_cell amount">${formatLang(tot_depreciated_value or '') | amount }</div>
                              <div class="act_as_cell amount">${formatLang(tot_amount or '') | amount }</div>
                              <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(line.get('tot_remaining_value') or '') | amount }</div>
                            </div>
                        </div>
                    </div>
                </div>
    
            <div class="act_as_table list_table" style="margin-top:5px;">
                <div class="act_as_row labels" style="font-weight: bold; font-size: 12px;">
                        <div class="act_as_cell first_column" style="width: 40px;">Totale</div>
                        <div class="act_as_cell" style="width: 50px;">${tot_cat_name}</div>
                        <div class="act_as_cell amount" style="width: 40px;">${formatLang(tot_cat_value or '') | amount }</div>
                        <div class="act_as_cell" style="width: 60px;"></div>
                        <div class="act_as_cell amount" style="width: 90px;">${formatLang(tot_cat_depreciated_value or '') | amount }</div>
                        <div class="act_as_cell amount" style="width: 90px;">${formatLang(tot_cat_amount or '') | amount }</div>
                        <div class="act_as_cell amount" style="width: 90px; padding-right: 1px;"></div>
                    </div>
                </div>
            </div>
    
        %endif

    <%
        if flag_print_final == True:
            print_info = set_print_info(fiscalyear_id, progr_row, progr_page)
    %>

</body>
</html>
