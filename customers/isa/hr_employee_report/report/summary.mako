<html>

<head>
  <style type="text/css">
/*<![CDATA[*/
        @page {  }
        table { border-collapse:collapse; border-spacing:0; empty-cells:show }
        td, th { vertical-align:top; font-size:12pt;}
        h1, h2, h3, h4, h5, h6 { clear:both }
        ol, ul { margin:0; padding:0;}
        li { list-style: none; margin:0; padding:0;}
        <!-- "li span.odfLiEnd" - IE 7 issue-->
        li span. { clear: both; line-height:0; width:0; height:0; margin:0; padding:0; }
        span.footnodeNumber { padding-right:1em; }
        span.annotation_style_by_filter { font-size:95%; font-family:Arial; background-color:#fff000;  margin:0; border:0; padding:0;  }
        * { margin:0;}
        .P1 { font-size:10pt; font-family:Liberation Serif; writing-mode:page; }
        .P10 { font-size:10pt; font-family:Liberation Serif; writing-mode:page; font-weight:bold; }
        .P11 { font-size:10pt; font-family:Liberation Serif; writing-mode:page; }
        .P12 { font-size:2pt; font-family:Liberation Serif; writing-mode:page; }
        .P13 { font-size:10pt; font-family:Liberation Serif; writing-mode:page; background-color:transparent; }
        .P2 { font-size:10pt; font-family:Liberation Serif; writing-mode:page; font-weight:bold; }
        .P3 { font-size:10pt; font-family:Liberation Serif; writing-mode:page; text-align:center ! important; font-weight:bold; }
        .P4 { font-size:6pt; font-family:Liberation Serif; writing-mode:page; }
        .P5 { font-size:9pt; font-family:LMMono10; writing-mode:page; }
        .P6 { font-size:10pt; font-family:Liberation Serif; writing-mode:page; background-color:#e6e6e6; }
        .P7 { font-size:11pt; font-family:Liberation Serif; writing-mode:page; background-color:#e6e6e6; font-weight:bold; }
        .P8 { font-size:12pt; font-family:LMMono10; writing-mode:page; background-color:#e6e6ff; font-weight:bold; }
        .P9 { font-size:8pt; font-family:Liberation Serif; writing-mode:page; background-color:#e6e6ff; }
        .Standard { font-size:12pt; font-family:Liberation Serif; writing-mode:page; }

        .T1 { font-family:Arial; font-size:8pt; }
        <!-- ODF styles with no properties representable as CSS -->
        .Table1.1 .Table1.10 .Table1.11 .Table1.12 .Table1.13 .Table1.14 .Table1.15 .Table1.16 .Table1.17 .Table1.3 .Table1.4 .Table1.5 .Table1.6 .Table1.7 .Table1.8 .Table1.9 { }
  /*]]>*/
  </style>
</head>

<body class="c24">

    <% setLang("it_IT") %>
    <% get_wizard_params(data["form"]["month"],data["form"]["year"],data["form"]["print_holidays"],data["form"]["print_attendances"],data["form"]["print_overtime"]) %>

  <table border="1" cellspacing="0" cellpadding="2" class="Table1">

    <tr class="Table11">
      <td colspan="14" class="Table1_A1 c17">
        <p class="P8">${_('PRESENZE, PERMESSI E STRAORDINARI')}</p>
      </td>
    </tr>

    <tr class="Table11">

    %for emp in get_emps():

    <tr class="Table14">
      <td colspan="14" class="Table1_B4 c19">
        <p class="P9">${get_holidays_by_month(emp['id']) or '&nbsp;'}</p>

        <p class="P9">${get_all_attendances(emp['id']) or '&nbsp;'}</p>

        <p class="P9">${get_all_attendances_normalized(emp['id']) and '&nbsp;'}</p>

        <p class="P9">${get_overtime_by_month(emp['id']) or '&nbsp;'}</p>

        <p class="P7">${emp['name']}</p>
      </td>
    </tr>

    <tr class="Table11">

      <td colspan="2" class="Table1_A1 c19">
        <p class="P10">${get_date()}</p>
      </td>

      %for day in get_days():
      <td class="Table1_A1 c21">
            <p class="P6">${day}</p>
      </td>
      %endfor

      <td class="Table1_G2 c18">
        <p class="P3">${_('Tot.')}</p>
      </td>
    </tr>

    %if get_print_holidays():
    %for hol_type in get_holiday_type():
    %if get_totals_by_type(hol_type['id']):

    <tr class="Table17">

      <td colspan="2" class="Table1_B9 c19">
        <p class="P1">${hol_type['name']}</p>
      </td>

      %for hol in get_holidays_by_type(hol_type['id']):

      <td class="Table1_E7 c21">
        <p class="P1">${hol}</p>
      </td>

      %endfor

      <td class="Table1_G10 c18">
        <p class="P2">${get_totals_by_type(hol_type['id'])}</p>
      </td>
    </tr>

    %endif
    %endfor
    %endif

    %if get_print_attendances():
    <tr class="Table110">

      <td colspan="2" class="Table1_A1 c19">
        <p class="P1">${_('Presenze effettive')}</p>
      </td>

      %for att in get_attendances():

      <td class="Table1_A1 c21">
        <p class="P1">${att}</p>
      </td>

      %endfor

      <td class="Table1_G10 c18">
        <p class="P2">${get_total_att()}</p>
      </td>
    </tr>

    <tr class="Table111">

      <td colspan="2" class="Table1_G1 c19">
        <p class="P1">${_('Presenze normaliz.')}</p>
      </td>

      %for att in get_attendances_normalized():

      <td class="Table1_G1 c21">
        <p class="P1">${att}</p>
      </td>

      %endfor

      <td class="Table1_G16 c18">
        <p class="P2">${get_total_att_normalized()}</p>
      </td>
    </tr>
    %endif

    %if get_print_overtime():
    %for ot_type in get_overtime_type():
    %if get_totals_ot_by_type(ot_type['id']):

    <tr class="Table114">

      <td colspan="2" class="Table1_G1 c19">
        <p class="P1">${ot_type['name']}</p>
      </td>

      %for overt in get_overtime_by_type(ot_type['id']):

      <td class="Table1_G1 c21">
        <p class="P1">${overt}</p>
      </td>

      %endfor

      <td class="Table1_G16 c18">
        <p class="P2">${get_totals_ot_by_type(ot_type['id'])}</p>
      </td>
    </tr>

    %endif
    %endfor
    %endif

    %endfor
  </table>

</body>
</html>
