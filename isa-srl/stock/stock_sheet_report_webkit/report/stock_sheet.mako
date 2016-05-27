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

.style-r2 {
    background-color: #efefef;
}
        </style>
    </head>
    <body>

  <%!
          def quantity(text):
              return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
  %>
	
	<%setLang(user.lang)%>

    <% get_wizard_params(data["form"]["date_from"],data["form"]["date_to"],data["form"]["product_id"][0],data["form"]["warehouse_id"][0]) %>
    <% get_start_line() %>


  <div class="account_title bg" style="width: 1080px; margin-top: 20px; font-size: 12px;">${_('Product')}:   ${data["form"]["product_id"][1] or ''}</div>

        <div class="act_as_table list_table" style="margin-top: 10px;">
                        
            <div class="act_as_caption account_title">
                Periodo di stampa dal ${data["form"]["date_from"] and (formatLang(data["form"]["date_from"], date=True))} al ${data["form"]["date_to"] and (formatLang(data["form"]["date_to"], date=True))}
            </div>

            <div class="act_as_thead">
                <div class="act_as_row labels">
                    <div class="act_as_cell first_column" style="width: 50px;">Data</div>
                    <div class="act_as_cell" style="width: 70px;">Numero Documento</div>
                    <div class="act_as_cell" style="width: 70px;">Partner</div>
                    <div class="act_as_cell" style="width: 70px;">Causale</div>
                    <div class="act_as_cell" style="width: 60px;">Unità di Misura</div>
                    <div class="act_as_cell amount" style="width: 250px;">Quantità</div>
                    <div class="act_as_cell" style="width: 60px;">Magazzino</div>
                    <div class="act_as_cell" style="width: 80px;">Documento Originale</div>
                    <div class="act_as_cell" style="width: 80px;">Progressivo</div>
                </div>

                <div class="act_as_row lines">
                    <div class="act_as_cell first_column">${data["form"]["date_from"] and (formatLang(data["form"]["date_from"], date=True))}</div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell">${_('Quantità Iniziale')}</div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell amount">
                        %if get_start_quantity():
                            ${formatLang(get_start_quantity()) | quantity}
                        %endif
                    </div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell"></div>
                </div>

                <% _last_balance = get_start_quantity() %>
                %for line in get_move_line():

                    <div class="act_as_row lines">
                        <div class="act_as_cell first_column">${line.date and (formatLang(line.date, date=True)) or ''}</div>
                        <div class="act_as_cell">${line.picking_id.ddt_id and line.picking_id.ddt_id.ddt_number or 'stock'}</div>
                        <div class="act_as_cell">${line.picking_id.partner_id.name or ''}</div>
                        <div class="act_as_cell">${line.picking_id.picking_type_id.name or ''}</div>
                        <div class="act_as_cell">${line.product_uom.name or ''}</div>
                        <div class="act_as_cell amount">
                            %if line.product_qty:
                                %if line.picking_id.picking_type_id.code == 'outgoing':
                                    -
                                %endif
                                ${formatLang(line.product_qty) | quantity}
                            %endif
                        </div>
                        <div class="act_as_cell">Magazzino</div>
                        <div class="act_as_cell">${line.origin or ''}</div>
                        <div class="act_as_cell">
                            %if line.picking_id.picking_type_id.code == 'outgoing': 
                                ${formatLang(_last_balance - line.product_qty - get_start_quantity()) | quantity}
                            %else:
                                ${formatLang(_last_balance + line.product_qty - get_start_quantity()) | quantity}
                            %endif
                        </div>
                    </div>

                    %if line.picking_id.picking_type_id.code == 'outgoing':
                        <% _last_balance = _last_balance - line.product_qty %>
                    %else:
                        <% _last_balance = _last_balance + line.product_qty %>
                    %endif
                %endfor

                <div class="act_as_row lines">
                    <div class="act_as_cell first_column"><b>${data["form"]["date_to"] and (formatLang(data["form"]["date_to"], date=True))}</b></div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell"><b>${_('Quantità Finale')}</b></div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell amount"><b>
                        %if get_totals_quantity():
                            ${formatLang(get_totals_quantity()) | quantity}
                        %endif
                    </b></div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell"></div>
                    <div class="act_as_cell"></div>
                </div>

            </div>
        </div>

</body>
</html>
