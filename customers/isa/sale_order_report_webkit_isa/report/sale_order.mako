<html>
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>

  <style type="text/css">

.style-0 {
    table-layout: fixed; 
    width: 1100pt
}

.style-01 {
    border-bottom: 1 pt solid black;
    border-left: 1 pt solid black;
    border-right: none;
    border-top: 1 pt solid black;
}

.style-011 {
    border-bottom: 1 pt solid black;
    border-right: 1 pt solid black;
    border-left: 1 pt solid black;
    border-top: 1 pt solid black;
}

.style-02 {
    page-break-inside: auto;
    page-break-before: auto;
    page-break-after: avoid;
}

.table_header {
    color: black;
    font-size: 13pt;
    font-family: "Arial";
    font-weight: bold;
    font-style: normal;
    text-decoration: none;
    text-align: left;
    word-spacing: 0pt;
    letter-spacing: 0pt;
    white-space: pre-wrap;
    border-top: 0.8pt solid black;
    border-bottom: 0.8pt solid black;
    border-left: 0pt;
    border-right: 0pt;
    padding: 3pt;
}

.table_row_grey {
    color: black;
    padding-left: 3pt;
    font-size: 12pt;
    font-family: "Arial";
    font-weight: normal;
    font-style: normal;
    text-decoration: none;
    text-align: left;
    word-spacing: 0pt;
    letter-spacing: 0pt;
    background-color: #efefef;
    padding: 3pt;
}

.table_row_white {
    color: black;
    padding-left: 3pt;
    font-size: 12pt;
    font-family: "Arial";
    font-weight: normal;
    font-style: normal;
    text-decoration: none;
    text-align: left;
    word-spacing: 0pt;
    letter-spacing: 0pt;
    background-color: #ffffff;
    padding: 3pt;
}

.c14 {border: 1px solid black; padding: 0in}
.c23 {border: none; padding: 0.06in}
.c4 {margin-bottom: -0.17in; margin-top: 0in; margin-left: 0.1in; margin-right: -0in;}
.c41 {margin-bottom: -0.17in; margin-top: -0.1in; margin-left: 0.1in; margin-right: -0in;}
.c5 {margin-top: -0.1in; margin-left: 0.1in; margin-right: 1in; padding-left: 100pt;}
.c3 {margin-left: 0.1in; margin-right: -0in; margin-top: -0.1in; font-style: normal; font-weight: normal}
.c2 {margin-left: 0.11in; margin-bottom: 0in; font-style: normal; font-weight: normal}
.c1 {margin-left: 0in; margin-right: 0in; font-style: normal}
.c6 {font-family: Arial, sans-serif; font-style: normal; font-weight: normal; font-size: 14pt;}
.c7 {font-family: Arial, sans-serif; font-style: normal; font-weight: normal; font-size: 11pt; }
.c121 {background: transparent; font-family: Arial, sans-serif; font-size: 12pt; font-style: normal; font-weight: bold}
.c91 {font-family: Arial; font-size: 12pt; font-style: normal; font-weight: bold}
.c22 {font-family: Arial, sans-serif; margin-left: 0.1in; margin-right: -0in; text-align: left}
.c44 {font-family: Arial, sans-serif; font-weight: normal; text-align: left}
.c25 {font-size: 8pt; text-align: left}
.c441 {border-top: none; border-bottom: 1px solid black; border-left: 1px solid black; border-right: none; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.02in; padding-right: 0in}
.c411 {border: 1px solid black; padding: 0.02in}
.c412 {border-top: none; border-bottom: none; border-left: 1px solid black; border-right: 1px solid black; padding: 0.02in}
.c401 {border-top: 1px solid black; border-bottom: 1px solid black; border-left: 1px solid black; border-right: none; padding-top: 0.02in; padding-bottom: 0.02in; padding-left: 0.02in; padding-right: 0in}
.c45 {border-top: none; border-bottom: 1px solid black; border-left: 1px solid black; border-right: 1px solid black; padding-top: 0in; padding-bottom: 0.02in; padding-left: 0.02in; padding-right: 0.02in}  
.c27 {font-family: Arial, sans-serif}
.c26 {font-size: 10pt}
.c20 {font-family: Arial, sans-serif; font-size: 12pt; font-weight: normal; font-style: normal; text-decoration: none; text-align: left; padding-left: 2pt; }
.c21 {font-family: Arial, sans-serif; font-size: 12pt; font-weight: normal; font-style: normal; text-decoration: none; text-align: right; padding-right: 2pt; }

  </style>
</head>

<body>
  <%!
          def amount(text):
              return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
  %>
  <%
          def carriage_returns(text):
              return text.replace('\n', '<br />')
  %>
  %for o in get_order(data['context']):
      <% setLang("it_IT") %>
      <% t_limit = data["form"]["rows_per_page"] %>
      <% t_font_description = data["form"]["font_description"] %>
      <% t_line_description = data["form"]["line_description"] %>

      <% num_pages = 2 + count_lines(o.id)/t_limit %>

      %for i in range(1, num_pages):

  <div type="HEADER">
    <table width="2800" border="0" cellpadding="0" cellspacing="0">
      <tr>
         <td width="300">
         
<img width="220" alt="" src="data:image/jpg;base64,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"/>

        </td>
        <td width="800">
            <span class="c6" style="font-size: 14pt;" style="text-align: right;">Business Support Solutions</span>
        </td>
      </tr>
        <tr>
            <td><span class="c6" style="font-size: 14pt;">${company.partner_id.name or ''|entity}</span></td>
        </tr>
        <tr>
            <td><span class="c6" style="font-size: 14pt;">${company.partner_id.street or ''|entity} ${company.partner_id.street2 or ''|entity}</span></td>
        </tr>
        <tr>
            <td><span class="c6" style="font-size: 14pt;">${company.partner_id.zip or ''|entity} ${company.partner_id.city or ''|entity}</span></td>
        </tr>
        <tr>
            <td><span class="c6" style="font-size: 14pt;">P. IVA: ${company.vat or company.partner_id.vat or ''|entity} CF: ${company.partner_id.fiscalcode or ''|entity}</span></td>
        </tr>

    </table>
    <br>
    <table width="1100" cellpadding="0" cellspacing="0">

      <tr valign="top">
        <td width="550" class="c23">
          <table width="100%" cellpadding="11" cellspacing="0">
            <tr>
                <td colspan="2" height="20" class="c401" style="border-bottom: none;">
                    <p class="c27"><span class="c26">Documento</span></p>
                    %if (o.state in ['draft','sent']):
                        <span class="c20">Preventivo</span>
                    %else:
                        <span class="c20">Ordine</span>
                    %endif
                </td>
                <td colspan="1" height="20" class="c401" style="border-bottom: none;">
                    <p class="c27"><span class="c26">Numero</span></p>
                    <span class="c20">${o.name or 'BOZZA'|entity}</span>
                </td>
                <td colspan="1" height="20" class="c411" style="border-bottom: none;">
                    <p class="c27"><span class="c26">Data</span></p>
                    <span class="c20">${o.date_order and (formatLang(o.date_order, date=True)) or ''|entity}</span>
                </td>
            </tr>
            <tr>
                <td colspan="2" height="20" class="c401" style="border-bottom: none;">
                    <p class="c27"><span class="c26">Partita IVA</span></p>
                    <span class="c20">${o.partner_id.vat or ''|entity}</span>
                </td>
                <td colspan="2" height="20" class="c411" style="border-bottom: none;">
                    <p class="c27"><span class="c26">Codice Fiscale</span></p>
                    <span class="c20">${o.partner_id.fiscalcode or ''|entity}</span>
                </td>
            </tr>
            <tr>
                <td colspan="4" height="20" class="c411" style="border-bottom: none;">
                <p class="c27"><span class="c26">Pagamento</span></p>
                <span class="c20">${o.payment_term and o.payment_term.name or ''|entity}</span>
                </td>
            </tr>
            <tr>
                <td colspan="4" height="20" class="c411" style="border-bottom: none;">
                <p class="c27"><span class="c26">Riferimento cliente</span></p>
                <span class="c20">${o.client_order_ref or ''|entity}</span>
                </td>
            </tr>
            <tr>
                <td colspan="4" height="20" class="c411">
                <p class="c27"><span class="c26">Ref. commerciale</span></p>
                <span class="c20">${o.user_id and o.user_id.name or ''|entity}</span>
                </td>
            </tr>
          </table>
        </td>

        <td width="600" class="c23">

          <table width="100%" cellpadding="11" cellspacing="0">

            <tr width="100%" height="250">
              <td width="100%" height="250" valign="top" class="c14">
                
                %if (o.partner_shipping_id and o.partner_shipping_id.id != o.partner_id.id):
                
                <p class="c4"><span class="c7">Spett.le</span></p>

                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_id.title and o.partner_id.title.name or ''}
                              ${o.partner_id.name or ''}
                              %if (o.partner_id.parent_id):
                                  <br>${o.partner_id.parent_id.name or ''}
                              %endif
                              </span></p>

                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_id.street or ''}
                              ${o.partner_id.street2 or ''}</span></p>

                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_id.zip or ''}
                              ${o.partner_id.city or ''}</span></p>
                
                <p class="c4"><span class="c7">Destinazione Merce (se diversa dal committente)</span></p>
                <br>
                <br>
                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_shipping_id.title and o.partner_shipping_id.title.name or ''}
                              ${o.partner_shipping_id.name or ''}</span></p>

                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_shipping_id.street or ''}
                              ${o.partner_shipping_id.street2 or ''}</span></p>

                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_shipping_id.zip or ''}
                              ${o.partner_shipping_id.city or ''}</span></p>
                
                %else:
                <p class="c4"><span class="c7">Spett.le</span></p>

                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_id.title and o.partner_id.title.name or ''}
                              ${o.partner_id.name or ''}
                              %if (o.partner_id.parent_id):
                                  <br>${o.partner_id.parent_id.name or ''}
                              %endif
                              </span></p>

                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_id.street or ''}
                              ${o.partner_id.street2 or ''}</span></p>

                <p class="c5"><span class="c6" style="font-size: 16pt;">${o.partner_id.zip or ''}
                              ${o.partner_id.city or ''}</span></p>

                <p class="c16"><br /></p>

                <p class="c3"><br /></p>
                %endif
                
              </td>
            </tr>
          </table>
          <p><br /></p>
        </td>
      </tr>
    </table>
    <p class="c24"><br /></p>
  </div>

  <table width="1100" cellpadding="2" cellspacing="0" class="style-02">
    <thead>
        <tr valign="top" style="height: 13pt">
          <td valign="middle" class="table_header" width="56%" style="border-left: 0.8pt solid black; border-right: 0pt;">Descrizione</td>
          <td valign="middle" class="table_header" width="6%">UM</td>
          <td valign="middle" class="table_header" width="8%" style="text-align: right;">Quantità</td>
          <td valign="middle" class="table_header" width="8%" style="text-align: right;">Prezzo<br>Unitario</td>
          <td valign="middle" class="table_header" width="8%" style="text-align: right;">Importo<br>Netto</td>
          <td valign="middle" class="table_header" width="14%" style="text-align: right; border-right: 0.8pt solid black;">Imposta</td>
        </tr>
      </thead>
      <tbody>
      <% order_line_counter = 0 %>
      <% tot_items = 0 %>
      %for line in  get_order_line(o.id,t_limit,(i-1)*t_limit):
        %if not line.exclude_from_print:
	      %if order_line_counter % 2 == 0: 
	            <% t_style1 = "table_row_grey" %>
	      %else:
	            <% t_style1 = "table_row_white" %>
	      %endif
	      
	      <tr valign="top" style="height: 13pt">
	           <td valign="middle" class=${t_style1} style="border-left: 0.8pt solid black; border-right: none">${line.product_id.code or ''}
                 %if not t_line_description:
	               <span style="font-size: ${t_font_description}pt;">${line.product_id.description_sale or line.product_id.name or line.name or ''|carriage_returns}</span>
                 %else:
	               <span style="font-size: ${t_font_description}pt;">${line.name or line.product_id.name or ''|carriage_returns}</span>
	             %endif
	           </td>
	           <td valign="middle" class=${t_style1} style="border-left: none; border-right: none">${line.product_uom and line.product_uom.name or ''}</td>
	           <td valign="middle" class=${t_style1} style="border-left: none; border-right: none; text-align: right;">${formatLang(line.product_uom_qty) or 0.00}</td>
	           <td valign="middle" class=${t_style1} style="border-left: none; border-right: none; text-align: right;">${formatLang(line.price_unit) or ''}</td>
	           <td valign="middle" class=${t_style1} style="border-left: none; border-right: none; text-align: right;">${formatLang(line.price_subtotal) or ''}</td>
	           <td valign="middle" class=${t_style1} style="border-left: none; border-right: 0.8pt solid black; text-align: right; text-align: right;">${', '.join(map(lambda x: x.name, line.tax_id))}</td>
	      </tr>
	      <% order_line_counter += 1 %>
	    %endif
      %endfor
      
      <% t_max_range = t_limit - order_line_counter %>
      <% tot_items += line.price_subtotal %>
      
      %if (t_max_range > 0):
	      %for i in range(1,t_max_range) :
		            <% t_style1 = "table_row_white" %>
		      <tr style="height: 13pt">
		        <td valign="middle" class=${t_style1} style="border-bottom: none; border-left: 0.8pt solid black; border-right: none">${'<br>'}</td>
		        <td valign="middle" class=${t_style1} style="border-bottom: none; border-left: none; border-right: none">${'<br>'}</td>
		        <td valign="middle" class=${t_style1} style="border-bottom: none; border-left: none; border-right: none">${'<br>'}</td>
		        <td valign="middle" class=${t_style1} style="border-bottom: none; border-left: none; border-right: none">${'<br>'}</td>
		        <td valign="middle" class=${t_style1} style="border-bottom: none; border-left: none; border-right: none">${'<br>'}</td>
		        <td valign="middle" class=${t_style1} style="border-bottom: none; border-left: none; border-right: 0.8pt solid black">${'<br>'}</td>
		      </tr>
	      %endfor
      %endif
      %if i < num_pages-1:
          <tr style="height: 13pt">
            <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
            <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
            <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
            <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
            <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
            <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
          </tr>
           </tbody>
        </table>
          <p style="margin-bottom: 0in; page-break-after: always"></p>
      %else:
           </tbody>
        </table>
      %endif
      %endfor

  <table width="1100" cellpadding="4" cellspacing="0">
      <tr valign="top">
        <td width="100%" style="height: 50pt" class="c411">
          <p class="c27"><span class="c26">${_('Note')}</span></p>
          <p class="c20"><span style="font-size: ${t_font_description}pt;">${o.note or ''|carriage_returns}</span></p>
        </td>
      </tr>
  </table>
  <br>
  <div type="FOOTER">    
    <table width="1100" cellpadding="0" cellspacing="0">
      <tr valign="top">
        <td width="760" class="c23">
          <table width="100%" cellpadding="4" cellspacing="0">
            <tr valign="top">
              <td width="40%" class="c50" style="border-top: 0.8pt solid black; border-bottom: 0.8pt solid black; border-left: 0.8pt solid black; border-right: 0.8pt solid black;">
                <p class="c27"><span class="c26">${_('Data, timbro e firma per accettazione')}</span></p>
                <p class="c20" style="text-align: right;"><br><br><br></p>
              </td>
            </tr>
          </table>
        </td>
        <td width="600" class="c23">
          <table width="100%" cellpadding="4" cellspacing="0">
            <tr valign="top">
              <td width="20%" class="c50" style="border-top: 0.8pt solid black; border-bottom: 0.8pt solid black; border-left: 0.8pt solid black; border-right: none;">
                <p class="c27"><span class="c26">${_('Totale Imponibile')}</span></p>
                <p class="c20" style="text-align: right;">${formatLang(o.amount_untaxed, dp='Account', currency_obj=o.pricelist_id.currency_id) | amount}</p>
              </td>
              <td width="20%" class="c50" style="border-top: 0.8pt solid black; border-bottom: 0.8pt solid black; border-left: 0.8pt solid black; border-right: none;">
                <p class="c27"><span class="c26">${_('Totale Imposta')}</span></p>
                <p class="c20" style="text-align: right;">${formatLang(o.amount_tax, dp='Account', currency_obj=o.pricelist_id.currency_id) | amount}</p>
              </td>
              <td width="20%" class="c50" style="border-top: 0.8pt solid black; border-bottom: 0.8pt solid black; border-left: 0.8pt solid black; border-right: 0.8pt solid black;">
                <p class="c27"><span class="c26">${_('Totale Documento')}</span></p>
                <p class="c20" style="text-align: right;"><b>${formatLang(o.amount_total, dp='Account', currency_obj=o.pricelist_id.currency_id) | amount}</b></p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </div>
  %endfor
</body>
</html>
