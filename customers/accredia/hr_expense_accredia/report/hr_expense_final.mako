<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head>
<meta http-equiv="content-type" content="text/html; charset=windows-1252">
        <style type="text/css">
            .overflow_ellipsis {
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }

            

body, table, td, span, div {
    font-family: Helvetica, Arial;
}

.act_as_table {
    display: table;
}
.act_as_row  {
    display: table-row;
}
.act_as_cell {
    display: table-cell;
}
.act_as_thead {
    display: table-header-group;
}
.act_as_tbody {
    display: table-row-group;
}
.act_as_tfoot {
    display: table-footer-group;
}
.act_as_caption {
    display: table-caption;
}
act_as_colgroup {
    display: table-column-group;
}

.list_table, .data_table {
    width: 1080px;
    table-layout: fixed
}

.bg, .act_as_row.labels {
    background-color:#F0F0F0;
}

.list_table, .data_table, .list_table .act_as_row {
    border-left:0px;
    border-right:0px;
    text-align:left;
    font-size:9px;
    padding-right:3px;
    padding-left:3px;
    padding-top:2px;
    padding-bottom:2px;
    border-collapse:collapse;
}

.list_table .act_as_row.labels, .list_table .act_as_row.initial_balance, .list_table .act_as_row.lines {
    border-color:gray;
    border-bottom:1px solid lightGrey;
}

.data_table .act_as_cell {
    border: 1px solid lightGrey;
    text-align: center;
}

.data_table .act_as_cell, .list_table .act_as_cell {
    word-wrap: break-word;
}

.data_table .act_as_row.labels {
    font-weight: bold;
}

.initial_balance .act_as_cell {
    font-style:italic;
}

.account_title {
    font-size:10px;
    font-weight:bold;
    page-break-after: avoid;
}

.act_as_cell.amount {
    word-wrap:normal;
    text-align:right;
}

.list_table .act_as_cell{
    padding-left: 5px;
/*    border-right:1px solid lightGrey;  uncomment to active column lines */
}
.list_table .act_as_cell.first_column {
    padding-left: 0px;
/*    border-left:1px solid lightGrey; uncomment to active column lines */
}

.sep_left {
    border-left: 1px solid lightGrey;
}

.overflow_ellipsis {
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
}

.open_invoice_previous_line {
    font-style: italic;
}

.clearance_line {
    font-style: italic;
}


            
        </style>
    </head>
    <body>

        <%!
            def amount(text):
                return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>
        <%
        fiscalyear_id = "form" in data and data["form"]["fiscalyear"] or 0
        t_date_from = "form" in data and data["form"]["date_from"] or ''
        t_date_to = "form" in data and data["form"]["date_to"] or ''
        only_total = "form" in data and data["form"]["only_total"] or 0
        print_info = fiscalyear_id and get_print_info(fiscalyear_id) or ''
        result_rows = get_expense_lines(t_date_from,t_date_to)

        page_rows = 20
        
        num_rows = len(result_rows)
        num_row = 0
        new_page = True
        style = ""

        progr_page = 0
        progr_row = 0

        last_asset_header = 0
        flag_asset_header = True
        prev_line = None

        tot_value = 0.0
        tot_amount = 0.0
        tot_depreciated_value = 0.0
        tot_remaining_value = 0.0

        tot_km = 0.0
        tot_car_own = 0.0
        tot_airplane_train = 0.0
        tot_public_transport = 0.0
        tot_highway = 0.0
        tot_car_rent = 0.0
        tot_restaurant = 0.0
        tot_hotel = 0.0
        tot_parking = 0.0
        tot_other = 0.0
        tot = 0.0
        %>
        <%setLang(user.lang)%>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell">${_('Anno Fiscale')}</div>
                <div class="act_as_cell">${_('Periodo')}</div>
                <div class="act_as_cell">${_('Dipendenti')}</div>
                <div class="act_as_cell">${_('Mostra Righe')}</div>
                <div class="act_as_cell"></div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${print_info and print_info['year_name'] or ''}</div>
                <div class="act_as_cell">${t_date_from and 'Da' or ''} ${t_date_from or ''} ${t_date_to and 'a' or ''} ${t_date_to or ''}</div>
                <div class="act_as_cell">Tutti</div>
                <div class="act_as_cell">${only_total and 'Solo Consuntivo' or 'Dettagliate'}</div>
                <div class="act_as_cell"><br></div>
            </div>
        </div>

        %for line in result_rows :
            %if last_asset_header != 0 and last_asset_header != line.get('employee_id'):
                        <div class="act_as_row lines labels">
                            <div class="act_as_cell first_column"><b></b></div>
                            <div class="act_as_cell"><b>${tot_km or ''}</b></div>
                            <div class="act_as_cell amount"><b>${tot_car_own and formatLang(tot_car_own) or '' | amount}</b></div>
                            <div class="act_as_cell amount"><b>${tot_airplane_train and formatLang(tot_airplane_train) or '' | amount}</b></div>
                            <div class="act_as_cell amount"><b>${tot_public_transport and formatLang(tot_public_transport) or '' | amount}</b></div>
                            <div class="act_as_cell amount"><b>${tot_highway and formatLang(tot_highway) or '' | amount}</b></div>
                            <div class="act_as_cell amount"><b>${tot_car_rent and formatLang(tot_car_rent) or '' | amount}</b></div>
                            <div class="act_as_cell amount"><b>${tot_restaurant and formatLang(tot_restaurant) or '' | amount}</b></div>
                            <div class="act_as_cell amount"><b>${tot_hotel and formatLang(tot_hotel) or '' | amount}</b></div>
                            <div class="act_as_cell amount"><b>${tot_parking and formatLang(tot_parking) or '' | amount}</b></div>
                            <div class="act_as_cell amount"><b>${tot_other and formatLang(tot_other) or '' | amount}</b></div>
                            <div class="act_as_cell amount" style="padding-right: 1px;"><b>${tot and formatLang(tot) or '' | amount}</b></div>
                      </div>
    
                    </div>
                </div>
                <%
                    tot_km = 0.0
                    tot_car_own = 0.0
                    tot_airplane_train = 0.0
                    tot_public_transport = 0.0
                    tot_highway = 0.0
                    tot_car_rent = 0.0
                    tot_restaurant = 0.0
                    tot_hotel = 0.0
                    tot_parking = 0.0
                    tot_other = 0.0
                    tot = 0.0
                %>
            %endif

            %if last_asset_header == 0 or last_asset_header != line.get('employee_id'):
                <div class="account_title bg" style="width: 1080px; margin-top: 20px; font-size: 12px;">${ line.get('employee_name') or ''|entity }</div>

            %endif



            %if last_asset_header == 0 or last_asset_header != line.get('employee_id'):
                <div class="act_as_table list_table" style="margin-top: 10px;">
                    
                    <div class="act_as_caption account_title">
                    </div>
    
                    <div class="act_as_thead">
                        <div class="act_as_row labels">
                            <div class="act_as_cell first_column" style="width: 50px;">Data</div>
                            <div class="act_as_cell amount" style="width: 70px;">Rimb. Auto &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Km</div>
                            <div class="act_as_cell amount" style="width: 70px;">Rimb. Auto &nbsp;&nbsp;&nbsp;&nbsp; Totale</div>
                            <div class="act_as_cell amount" style="width: 80px;">Aereo/Treno</div>
                            <div class="act_as_cell amount" style="width: 80px;">Metro/Taxi</div>
                            <div class="act_as_cell amount" style="width: 80px;">Autostrada</div>
                            <div class="act_as_cell amount" style="width: 80px;">Noleggio Auto</div>
                            <div class="act_as_cell amount" style="width: 80px;">Ristorante/Bar</div>
                            <div class="act_as_cell amount" style="width: 80px;">Hotel</div>
                            <div class="act_as_cell amount" style="width: 80px;">Parcheggio</div>
                            <div class="act_as_cell amount" style="width: 80px;">Altre Spese</div>
                            <div class="act_as_cell amount" style="width: 80px;">Rimborso Dipendente</div>
                        </div>
                    </div>

                    <div class="act_as_tbody">
                    <%
                        last_asset_header = line.get('employee_id')
                        flag_asset_header = True
                    %>

            %endif

            %if not only_total:
                %if line.get('expense_type',False):
                    <div class="act_as_row lines">
                        <div class="act_as_cell first_column">${ formatLang(line.get('date'), date=True) or ''|entity }</div>
                        <div class="act_as_cell">${line.get('expense_type') == 'car_own' and line.get('unit_quantity') or '' | entity}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'car_own' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'airplane_train' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'public_transport' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'highway' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'car_rent' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'restaurant' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'hotel' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'parking' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount">${line.get('expense_type') == 'other' and formatLang(line.get('price_total')) or '' | amount}</div>
                        <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(line.get('price_total')) or '' | amount}</div>
                    </div>
                %endif
            %endif
            <%
            prev_line = line
            %>

            %if line.get('expense_type',False):
            <%
                tot_km               = tot_km +               (line.get('expense_type') == 'car_own' and line.get('unit_quantity') or 0.0)
                tot_car_own          = tot_car_own +          (line.get('expense_type') == 'car_own' and line.get('price_total') or 0.0)
                tot_airplane_train   = tot_airplane_train +   (line.get('expense_type') == 'airplane_train' and line.get('price_total') or 0.0)
                tot_public_transport = tot_public_transport + (line.get('expense_type') == 'public_transport' and line.get('price_total') or 0.0)
                tot_highway          = tot_highway +          (line.get('expense_type') == 'highway' and line.get('price_total') or 0.0)
                tot_car_rent         = tot_car_rent +         (line.get('expense_type') == 'car_rent' and line.get('price_total') or 0.0)
                tot_restaurant       = tot_restaurant +       (line.get('expense_type') == 'restaurant' and line.get('price_total') or 0.0)
                tot_hotel            = tot_hotel +            (line.get('expense_type') == 'hotel' and line.get('price_total') or 0.0)
                tot_parking          = tot_parking +          (line.get('expense_type') == 'parking' and line.get('price_total') or 0.0)
                tot_other            = tot_other +            (line.get('expense_type') == 'other' and line.get('price_total') or 0.0)
                tot                  = tot +                  (not line.get('already_paid') and line.get('price_total') or 0.0)
            %>
            %endif

        %endfor

        %if prev_line:

                            <div class="act_as_row lines labels">
                                <div class="act_as_cell first_column"><b></b></div>
                                <div class="act_as_cell"><b>${tot_km or ''}</b></div>
                                <div class="act_as_cell amount"><b>${tot_car_own and formatLang(tot_car_own) or '' | amount}</b></div>
                                <div class="act_as_cell amount"><b>${tot_airplane_train and formatLang(tot_airplane_train) or '' | amount}</b></div>
                                <div class="act_as_cell amount"><b>${tot_public_transport and formatLang(tot_public_transport) or '' | amount}</b></div>
                                <div class="act_as_cell amount"><b>${tot_highway and formatLang(tot_highway) or '' | amount}</b></div>
                                <div class="act_as_cell amount"><b>${tot_car_rent and formatLang(tot_car_rent) or '' | amount}</b></div>
                                <div class="act_as_cell amount"><b>${tot_restaurant and formatLang(tot_restaurant) or '' | amount}</b></div>
                                <div class="act_as_cell amount"><b>${tot_hotel and formatLang(tot_hotel) or '' | amount}</b></div>
                                <div class="act_as_cell amount"><b>${tot_parking and formatLang(tot_parking) or '' | amount}</b></div>
                                <div class="act_as_cell amount"><b>${tot_other and formatLang(tot_other) or '' | amount}</b></div>
                                <div class="act_as_cell amount" style="padding-right: 1px;"><b>${tot and formatLang(tot) or '' | amount}</b></div>
                          </div>
        
                    </div>
                </div>

        %endif


</body></html>