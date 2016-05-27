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
    <% get_wizard_params(data["form"]["month"],data["form"]["year"]) %>

  <table border="1" cellspacing="0" cellpadding="2" class="Table1">

    <tr class="Table11">
      <td colspan="14" class="Table1_A1 c17">
        <p class="P8">${_('REPORT PRESENZE')}</p>
      </td>
    </tr>

    <tr class="Table11">

      <td colspan="2" class="Table1_A2 c19">
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

    %for emp in get_emps():

    <tr class="Table14">
      <td colspan="19" class="Table1_B4 c19">
        <p class="P7">${emp['name']} ${get_total_attendance(emp['id']) or ''}</p>
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

    <tr class="Table114">

      <td colspan="2" class="Table1_G1 c19">
        <p class="P1">${_('Presenze effettive')}</p>
      </td>

      %for att in get_day_attendance():

      <td class="Table1_G1 c21">
        <p class="P1">${att}</p>
      </td>

      %endfor

      <td class="Table1_G16 c18">
        <p class="P2">${get_total()}</p>
      </td>
    </tr>

    %endfor
  </table>
</body>
</html>
