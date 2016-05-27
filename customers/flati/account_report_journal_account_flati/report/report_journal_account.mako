<html>
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
    
  <style type="text/css">

.style-3 {
    color: black; 
    font-size: 18pt; 
    font-family: "Arial"; 
    font-weight: bold; 
    font-style: normal; 
    text-decoration: none; 
    text-align: left; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    white-space: pre-wrap
}

.style-4 {
    color: black; 
    font-size: 18pt; 
    font-family: "Arial"; 
    font-weight: bold; 
}

.style-5 {
    color: black;
    font-size: 8pt;
    font-family: "Arial";
    font-weight: bold;
    font-style: normal;
    text-decoration: none;
    text-align: center;
    border-top: 2pt solid black;
    border-left: 2pt solid black;
    border-bottom: 4pt solid black;
    border-right: 1pt solid black;
    height: 20pt;
    background-color: #eeeeff;
}

.style-6 {
    color: black; 
    font-size: 6pt; 
    font-family: "Arial"; 
    font-weight: bold; 
    font-style: normal; 
    text-decoration: none; 
    text-align: center; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    white-space: pre-wrap; 
    border-top: 1pt solid black; 
    border-left: 1pt solid black; 
    border-bottom: 2pt solid black
}

.style-7 {
    color: black; 
    font-size: 6pt; 
    font-family: "Arial"; 
    font-weight: bold; 
    font-style: normal; 
    text-decoration: none; 
    text-align: center; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    white-space: pre-wrap; 
    border-top: 1pt solid black; 
    border-bottom: 2pt solid black; 
    border-right: 1pt solid black
}

.style-9 {
    font-size: 1pt; 
    border-top: 1pt solid black; 
    border-bottom: 1pt solid black
}

.style-10 {
    color: black; 
    padding-right: 5pt; 
    font-size: 9pt; 
    font-family: "Arial"; 
    font-weight: normal; 
    font-style: italic; 
    text-decoration: none; 
    text-align: right; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    white-space: pre-wrap; 
    border-top: 1pt solid black; 
    border-bottom: 2pt solid black
}

.style-r1 {
    background-color: #ffffff;
}

.style-r2 {
    background-color: #efefef;
}

.style-11 {
    color: black; 
    padding-right: 5pt; 
    font-size: 9pt; 
    font-family: "Arial"; 
    font-weight: normal; 
    font-style: normal; 
    text-decoration: none; 
    text-align: center; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    border-left: 1pt solid black; 
    border-bottom: 0pt solid black; 
    border-right: 0pt black;
    height:20px;
    overflow:hidden;
    page-break-inside: avoid;
    o-text-overflow: clip;
    text-overflow: clip;
}

.style-12 {
    color: black; 
    padding-right: 5pt; 
    font-size: 9pt; 
    font-family: "Arial"; 
    font-weight: normal; 
    font-style: normal; 
    text-decoration: none; 
    text-align: center; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    border-left: 1pt solid black; 
    border-bottom: 0pt solid black; 
    border-right: 1pt solid black;
    height:20px;
    overflow:hidden;
    page-break-inside: avoid;
    o-text-overflow: clip;
    text-overflow: clip;
}

.style-22 {
    color: black; 
    font-size: 9pt; 
    font-family: "Arial"; 
    font-weight: bold; 
    font-style: normal; 
    text-decoration: none; 
    text-align: center; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    white-space: pre-wrap; 
    border: 1pt solid black
}

.style-23 {
    color: black; 
    padding-right: 5pt; 
    font-size: 9pt; 
    font-family: "Arial"; 
    font-weight: normal; 
    font-style: normal; 
    text-decoration: none; 
    text-align: right; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    white-space: pre-wrap; 
    border: 1pt solid black
}

.style-71 {
    color: black; 
    font-size: 6pt; 
    font-family: "Arial"; 
    font-weight: bold; 
    font-style: normal; 
    text-decoration: none; 
    text-align: center; 
    word-spacing: 0pt; 
    letter-spacing: 0pt; 
    white-space: pre-wrap;
    border-style:groove;
    border-width:2pt 1pt 1pt 1pt;
    border-color:black;
}

  </style>

</head>
<body>
  <% setLang("it_IT") %>
  <%!
          def amount(text):
              return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
  %>


<%  t_date_start = get_date_start() %>
<%  t_date_stop  = get_date_stop() %>


      <h3>${_('Bilancio del conto analitico')}</h3>

  <table width="1100" cellpadding="2" cellspacing="0">
    <thead>
      <tr valign="top" style="height: 10pt">
          <td valign="middle" class="style-5" style="text-align: left" width="25%">${_("Conto analitico")}</td>
          <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Data Doc")}</td>
          <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Numero Doc")}</td>
          <td valign="middle" class="style-5" style="text-align: left" width="9%" style="height:40px;">${_("Descrizione")}</td>
          <td valign="middle" class="style-5" width="9%" style="height:40px;">${_("Conto")}</td>
          <td valign="middle" class="style-5" width="5%" style="height:40px;">${_("Giornale<br>analitico")}</td>
          <td valign="middle" class="style-5" style="text-align: left" width="7%">${_("Partner")}</td>
          <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Costi")}</td>
          <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Ricavi")}</td>
          <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Margine")}</td>
      </tr>
    </thead>
    <tbody>
      <% row_count = 1 %>
      %for move in get_journal_moves(data['form'],data['context']):
          <tr valign="top">
              <td valign="middle" class="style-11" style="text-align: left">${move['an_ac_name']}</td>
              <td valign="middle" class="style-11" style="text-align: right">${formatLang(move['date'],date=True) or ''|entity}</td>
              <td valign="middle" class="style-11">
              %if move['ref'] != None:
                ${move['ref']}
              %endif
              </td>
              <td valign="middle" class="style-11" style="text-align: left">${move['desc']}</td>
              <td valign="middle" class="style-11">${move['code']}/${move['name']}</td>
              <td valign="middle" class="style-11">${move['journal']}</td>
              <td valign="middle" class="style-11" style="text-align: left">${move['partner'] or ''}</td>
              <td valign="middle" class="style-11" style="text-align: right">
                %if move['credit']:
                  ${formatLang(move['credit'], monetary=True, digits=get_digits(dp='Account')) | amount}
                %endif
                  </td>
              <td valign="middle" class="style-11" style="text-align: right">
                %if move['debit']:
                  ${formatLang(move['debit'], monetary=True, digits=get_digits(dp='Account')) | amount}
                %endif
                </td>
              <td valign="middle" class="style-12"></td>
          </tr>
          <% row_count = row_count + 1 %>
          %if row_count > 14:
            <% row_count = 1 %>
                </tbody>
              </table>
    
              <table width="1100" cellpadding="2" cellspacing="0" style="page-break-before: always">
                <thead>
                  <tr valign="top" style="height: 20pt">
                      <td valign="middle" class="style-5" style="text-align: left" width="25%" style="height:40px;">${_("Conto analitico")}</td>
                      <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Data Doc")}</td>
                      <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Numero Doc")}</td>
                      <td valign="middle" class="style-5" style="text-align: left" width="9%" style="height:40px;">${_("Descrizione")}</td>
                      <td valign="middle" class="style-5" width="9%" style="height:40px;">${_("Conto")}</td>
                      <td valign="middle" class="style-5" width="5%" style="height:40px;">${_("Giornale<br>analitico")}</td>
                      <td valign="middle" class="style-5" style="text-align: left" width="7%" style="height:40px;">${_("Partner")}</td>
                      <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Costi")}</td>
                      <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Ricavi")}</td>
                      <td valign="middle" class="style-5" width="7%" style="height:40px;">${_("Margine")}</td>
                  </tr>
                </thead>
                <tbody>
            
          %endif

      %endfor
      <tr>
        <td colspan="7" class="style-10">${_("Totale")}</td>
        <td colspan="1" class="style-10" style="text-align: right">${formatLang(get_journal_totals_credit(), monetary=True, digits=get_digits(dp='Account')) | amount}</td>
        <td colspan="1" class="style-10" style="text-align: right">${formatLang(get_journal_totals_debit(), monetary=True, digits=get_digits(dp='Account')) | amount}</td>
        <td colspan="1" class="style-10" style="text-align: right">${formatLang(get_journal_margins(), monetary=True, digits=get_digits(dp='Account')) | amount}</td>
      </tr>

    </tbody>
  </table>
</body>
</html>
