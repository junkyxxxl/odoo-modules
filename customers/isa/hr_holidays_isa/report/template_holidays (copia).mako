<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta name="generator" content=
  "HTML Tidy for Linux/x86 (vers 25 March 2009), see www.w3.org" />
  <style type="text/css">
/*<![CDATA[*/
  p.c9 {margin-bottom: 0cm}
  table.c8 {page-break-before: auto; page-break-after: auto; page-break-inside: auto}
  td.c7 {background-color: #CCCCFF}
  p.c6 {background: #e6e6ff}
  p.c5 {margin-bottom: 0cm; background: #e6e6e6}
  p.c4 {font-size: 80%; font-weight: bold; text-align: center}
  p.c3 {background: #e6e6e6}
  p.c2 {text-align: center}
  p.c1 {background: #e6e6ff; font-family: LMMono10; font-weight: bold}
  /*]]>*/
  </style>

  <title></title>
  <style type="text/css">
/*<![CDATA[*/
  p.c25 {margin-bottom: 0in; page-break-before: always}
  /*]]>*/
  </style>
</head>

<body>
  %for o in objects : <% setLang("it_IT") %>

  <table width="100%" border="1" bordercolor="#000000" cellpadding=
  "4" cellspacing="0" rules="ROWS" class="c8">
    <colgroup>
      <col width="14*" />
    </colgroup>

    <colgroup>
      <col width="88*" />
    </colgroup>

    <colgroup>
      <col width="76*" />
      <col width="14*" />
    </colgroup>

    <colgroup>
      <col width="33*" />
    </colgroup>

    <colgroup>
      <col width="30*" />
    </colgroup>

    <thead>
      <tr valign="top">
        <td colspan="5" width="88%" height="13">
          <p class="c1">${_('PERMESSI E STRAORDINARI')}</p>
        </td>

        <td width="12%">
          <p class="c2"><br /></p>
        </td>
      </tr>

      <tr valign="top">
        <td width="6%" height="13">
          <p><br /></p>
        </td>

        <td width="34%">
          <p>get_wizard_params get_date</p>
        </td>

        <td width="30%">
          <p>for days</p>
        </td>

        <td width="6%">
          <p class="c3">day</p>
        </td>

        <td width="13%">
          <p>&lt;/for&gt;</p>
        </td>

        <td width="12%">
          <p class="c4">Totale</p>
        </td>
      </tr>
    </thead>

    <tbody>
      <tr valign="top">
        <td rowspan="2" width="6%">
          <p>for emp</p>

          <p><br /></p>

          <p><br /></p>
        </td>

        <td colspan="4" width="82%">
          <p><br /></p>
        </td>

        <td rowspan="2" width="12%">
          <p><br /></p>
        </td>
      </tr>

      <tr valign="top">
        <td colspan="4" width="82%">
          <p class="c5">name</p>

          <p class="c6">get_holidays_by_month</p>
        </td>
      </tr>

      <tr valign="top">
        <td width="6%">
          <p><br /></p>
        </td>

        <td width="34%">
          <p>for get_holiday_type</p>
        </td>

        <td width="30%">
          <p><br /></p>
        </td>

        <td width="6%">
          <p><br /></p>
        </td>

        <td width="13%">
          <p><br /></p>
        </td>

        <td width="12%">
          <p><br /></p>
        </td>
      </tr>

      <tr valign="top">
        <td width="6%">
          <p><br /></p>
        </td>

        <td width="34%">
          <p>if get_totals_by_type</p>
        </td>

        <td width="30%">
          <p><br /></p>
        </td>

        <td width="6%">
          <p><br /></p>
        </td>

        <td width="13%">
          <p><br /></p>
        </td>

        <td width="12%">
          <p><br /></p>
        </td>
      </tr>

      <tr valign="top">
        <td width="6%">
          <p><br /></p>
        </td>

        <td width="34%">
          <p>hol_type.name</p>
        </td>

        <td width="30%">
          <p>for hol_by_type</p>
        </td>

        <td width="6%">
          <p>hol</p>
        </td>

        <td width="13%">
          <p>&lt;/for&gt;</p>
        </td>

        <td class="c7" width="12%">
          <p>get_totals_by_type</p>
        </td>
      </tr>

      <tr valign="top">
        <td rowspan="2" width="6%">
          <p><br /></p>
        </td>

        <td width="34%">
          <p>&lt;/if&gt;</p>
        </td>

        <td width="30%">
          <p><br /></p>
        </td>

        <td width="6%">
          <p><br /></p>
        </td>

        <td width="13%">
          <p><br /></p>
        </td>

        <td width="12%">
          <p><br /></p>
        </td>
      </tr>

      <tr valign="top">
        <td width="34%">
          <p>&lt;/for&gt;</p>
        </td>

        <td width="30%">
          <p><br /></p>
        </td>

        <td width="6%">
          <p><br /></p>
        </td>

        <td width="13%">
          <p><br /></p>
        </td>

        <td width="12%">
          <p><br /></p>
        </td>
      </tr>

      <tr valign="top">
        <td width="6%">
          <p>&lt;/for&gt;</p>
        </td>

        <td width="34%">
          <p><br /></p>
        </td>

        <td width="30%">
          <p><br /></p>
        </td>

        <td width="6%">
          <p><br /></p>
        </td>

        <td width="13%">
          <p><br /></p>
        </td>

        <td width="12%">
          <p><br /></p>
        </td>
      </tr>
    </tbody>
  </table>

  <p class="c9"><br /></p>

  <p class="c25"></p>%endfor
</body>
</html>
