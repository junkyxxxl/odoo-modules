## -*- coding: utf-8 -*-
<html>
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>

  <style type="text/css">

.style-0 {
    table-layout: fixed; 
    width: 800pt
}

.style-01 {
    border-bottom: 0.8pt solid black;
    border-left: 0.8pt solid black;
    border-right: none;
    border-top: 0.8pt solid black;
}

.style-011 {
    border-bottom: 0.8pt solid black;
    border-right: 0.8pt solid black;
    border-left: 0.8pt solid black;
    border-top: 0.8pt solid black;
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
    font-family: "Arial" [Seleziona data] ;
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
.c23 {border: none; padding: 0.12in}
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
.c25 {font-size: 16pt; text-align: left}
.c441 {border-top: none; border-bottom: 1px solid black; border-left: 1px solid black; border-right: none; padding-top: 0in; padding-bottom: 0.04in; padding-left: 0.04in; padding-right: 0in}
.c411 {border: 1px solid black; padding: 0.04in}
.c412 {border-top: none; border-bottom: none; border-left: 1px solid black; border-right: 1px solid black; padding: 0.04in}
.c401 {border-top: 1px solid black; border-bottom: 1px solid black; border-left: 1px solid black; border-right: none; padding-top: 0.04in; padding-bottom: 0.04in; padding-left: 0.04in; padding-right: 0in}
.c45 {border-top: none; border-bottom: 1px solid black; border-left: 1px solid black; border-right: 1px solid black; padding-top: 0in; padding-bottom: 0.04in; padding-left: 0.04in; padding-right: 0.04in}  
.c27 {font-family: Arial, sans-serif}
.c26 {font-size: 10pt}
.c20 {font-size: 12pt; font-weight: normal; font-style: normal; text-decoration: none; text-align: left; padding-left: 2pt; }
.c21 {font-size: 12pt; font-weight: normal; font-style: normal; text-decoration: none; text-align: right; padding-right: 2pt; }

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

<%def name="header(obj)">
  <div type="HEADER">

    <table border="0" cellpadding="0" cellspacing="0">
      <tr>
         <td>
<img width="180" alt="" src="data:image/*;base64,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"/>

        </td>
        <td>

        </td>
      </tr>
    </table>

<h2 align="center">Resoconto di Missione</h2>


  </div>
</%def>
  

  <% t_first = False %>
  <% t_limit = 30 %>

  %for o in objects:
    <% t_partner_list = get_partner_dict(o) %>
    %for t_partner_id in t_partner_list:
      <% setLang("it_IT") %>

        %for t_holiday_id in t_partner_list[t_partner_id]:
            %if t_first: 
                <p style="margin-bottom: 0in; page-break-before: always"></p>
            %endif
    
            <% t_first = True %>
    
            ${header(o)}
    
            <p>Il/La Sottocritto/a ${get_partner(t_partner_id).name or ''|entity}</p>
            <p>Partenza: ${get_hr_holidays(t_holiday_id).date_from or ''|entity}</p>
            <p>Rientro: ${get_hr_holidays(t_holiday_id).date_to or ''|entity}</p>
            <p>Dipartimento: ${get_hr_holidays(t_holiday_id).department_id.department_nick or ''|entity}</p>
            <p>Motivazione: ${get_hr_holidays(t_holiday_id).name or ''|entity}</p>

            <br/>

          <table width="100%" cellpadding="1" cellspacing="0" class="style-0">
            <thead>
                <tr valign="top" style="height: 13pt">
                  <td valign="middle" class="table_header" width="20%" style="border-left: 1pt solid black;">Giorno</td>
                  <td valign="middle" class="table_header" width="20%" style="text-align: left;">Inizio</td>
                  <td valign="middle" class="table_header" width="20%" style="text-align: left;">Fine</td>
                  <td valign="middle" class="table_header" width="39%" style="text-align: left;">Descrizione</td>
                  <td valign="middle" class="table_header" width="1%" style="text-align: right; border-right: 1pt solid black;"></td>
                </tr>
              </thead>
              <tbody>
              <% line_counter = 0 %>
              %for t_holiday_line in get_hr_holidays_line(t_holiday_id):

                   <tr valign="top" style="height: 13pt">
                    <td valign="middle" style="border-left: 1pt solid black; border-right: none; text-align: left;">${t_holiday_line.date_from and formatLang(t_holiday_line.date_from, date=True) or ''|entity}</td>
                    <td valign="middle" style="border-left: none; border-right: none; text-align: left;">${t_holiday_line.date_from and formatLang(t_holiday_line.date_from, date_time=True)[-8:] or ''|entity}</td>
                    <td valign="middle" style="border-left: none; border-right: none; text-align: left;">${t_holiday_line.date_to and formatLang(t_holiday_line.date_to, date_time=True)[-8:] or ''|entity}</td>
                    <td valign="middle" style="border-left: none; border-right: none; text-align: left;">${t_holiday_line.product_id and t_holiday_line.product_id.name or ''|entity}</td>
                    <td valign="middle" style="border-left: none; border-right: 1pt solid black; text-align: right; text-align: right;"></td>
                  </tr>

              <% line_counter += 1 %>
              %endfor
              
              <% t_max_range = t_limit - line_counter %>
              
              %if (t_max_range > 0):
                %for i in range(1,t_max_range) :
                <tr style="height: 13pt">
                  <td valign="middle" style="border-bottom: none; border-left: 0.8pt solid black; border-right: none">${'<br>'}</td>
                  <td valign="middle" style="border-bottom: none; border-left: none; border-right: none">${'<br>'}</td>
                  <td valign="middle" style="border-bottom: none; border-left: none; border-right: none">${'<br>'}</td>
                  <td valign="middle" style="border-bottom: none; border-left: none; border-right: none">${'<br>'}</td>
                  <td valign="middle" style="border-bottom: none; border-left: none; border-right: 0.8pt solid black">${'<br>'}</td>
                </tr>
                %endfor
              %endif

            <tr style="height: 13pt">
              <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
              <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
              <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
              <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
              <td valign="middle" class="table_row_white" style="border: none; border-top: 1pt solid black;"></td>
            </tr>
             </tbody>
          </table>

          <table width="100%" cellpadding="1" cellspacing="0">
            <tr valign="top">
              <td width="100%" style="height: 60pt;" class="c411">
                <p class="c27"><span class="c26">${_('Note')}</span></p>
                <p class="c20">${get_hr_holidays(t_holiday_id).note or ''|carriage_returns}</p>
              </td>
            </tr>
          </table>

          <br/><br/><br/><br/>

         <table align="left" width="800" border="0"
                cellpadding="0" cellspacing="2" style="font-size: 0.8em;">
            <tbody>
                <tr>
                    <td align="left" valign="top">&nbsp;</td>
                    <td align="right" valign="top">&nbsp;</td>
                    <td align="right" valign="top">&nbsp;</td>
                    <td align="left" valign="top">&nbsp;</td>
                    <td align="left" valign="top">&nbsp;</td>
                    <td align="center" valign="top" style="border-top: 1px solid black;">&nbsp;&nbsp;&nbsp;Data&nbsp;&nbsp;&nbsp;</td>
                    <td align="left" valign="top">&nbsp;</td>
                    <td align="left" valign="top">&nbsp;</td>
                    <td align="left" valign="top">&nbsp;</td>
                    <td align="center" valign="top" style="border-top: 1px solid black;">Firma ${get_partner(t_partner_id).name or ''}</td>
                    <td align="center" valign="top">&nbsp;</td>
                    <td align="center" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
                    <td align="center" valign="top">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
                </tr>
            </tbody>
        </table>
      %endfor

    %endfor
  %endfor
</body>
</html>
