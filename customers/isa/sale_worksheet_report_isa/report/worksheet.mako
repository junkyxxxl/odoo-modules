<html>
<head>
  <style type="text/css">
  table.c50 {page-break-before: auto}
  td.c49 {border: 1px solid #000000; padding: 0.04in}
  p.c48 {background: transparent; text-align: left}
  span.c47 {font-size: 9pt}
  table.c46 {page-break-before: auto; page-break-after: auto; page-break-inside: avoid}
  p.c45 {font-weight: normal; text-align: right}
  td.c44 {border-top: none; border-bottom: 1px solid #000000; border-left: none; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.04in; padding-left: 0in; padding-right: 0.04in}
  td.c43 {border-top: none; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000; padding-top: 0in; padding-bottom: 0.04in; padding-left: 0.04in; padding-right: 0.04in}
  td.c42 {background-color: #E6E6E6; border: 1px solid #000000; padding: 0.04in}
  td.c41 {background-color: #E6E6E6; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; border-top: 1px solid #000000; padding-bottom: 0.04in; padding-left: 0.04in; padding-right: 0in; padding-top: 0.04in}
  p.c40 {font-family: Helvetica, sans-serif; text-align: left}
  span.c39 {font-size: 8pt; font-weight: bold}
  p.c38 {margin-bottom: 0in}
  td.c37 {border: 1px solid #000000; padding: 0.02in}
  p.c36 {font-family: Helvetica, sans-serif; text-align: right}
  p.c35 {font-family: Helvetica, sans-serif}
  p.c34 {font-weight: normal; text-align: center}
  p.c33 {font-weight: normal; text-align: left}
  p.c32 {font-family: Arial, sans-serif; font-weight: normal; text-align: center}
  td.c31 {border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: none; padding-top: 0.02in; padding-bottom: 0.02in; padding-left: 0.02in; padding-right: 0in}
  p.c30 {text-align: center}
  p.c29 {text-align: left}
  p.c28 {font-family: Helvetica, sans-serif; font-weight: normal; text-align: left}
  span.c27 {font-size: 6pt}
  td.c26 {border: 1px solid #000000; padding: 0.12in}
  p.c25 {color: #1A1A1A; font-style: normal; font-weight: normal; margin-left: 0.1in; margin-right: -0in}
  span.c24 {font-family: Helvetica, sans-serif; font-size: 6pt}
  span.c23 {font-family: Arial, sans-serif; font-size: 8pt}
  p.c22 {color: #1A1A1A; font-style: normal; font-weight: normal; margin-left: 0.1in; margin-right: -0in; text-align: left}
  span.c21 {font-family: Arial, sans-serif; font-size: 80%}
  span.c20 {font-family: Helvetica, sans-serif; font-size: 8pt}
  span.c19 {font-family: Arial, sans-serif; font-weight: bold}
  p.c18 {font-family: Arial, sans-serif; margin-left: 0.1in; margin-right: -0in}
  span.c17 {font-size: 80%}
  span.c16 {background: transparent}
  p.c15 {margin-right: -0in}
  td.c14 {border: none; padding: 0in}
  p.c13 {font-style: normal; font-weight: normal}
  span.c12 {background: transparent; font-family: Arial, sans-serif; font-size: 8pt; font-style: normal; font-weight: normal}
  p.c11 {margin-left: 0.11in; margin-bottom: 0in}
  span.c10 {font-family: Helvetica, sans-serif; font-size: 8pt; font-style: normal; font-weight: normal}
  span.c9 {font-family: Hevetica; font-size: 8pt; font-style: normal; font-weight: normal}
  p.c8 {font-family: Hevetica; margin-bottom: 0in; margin-left: 0.11in}
  span.c7 {font-size: 8pt}
  span.c6 {font-family: Helvetica, sans-serif; font-style: normal; font-weight: normal}
  span.c5 {font-style: normal; font-weight: normal}
  p.c4 {margin-left: 0.1in; margin-right: -0in}
  p.c3 {margin-left: 0.1in; margin-right: -0in; font-style: normal; font-weight: normal}
  p.c2 {margin-left: 0.11in; margin-bottom: 0in; font-style: normal; font-weight: normal}
  p.c1 {margin-left: 0.1in; margin-right: -0in; font-style: normal}
  </style>
</head>

<body>
  <%!
          def amount(text):
              return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
  %>
  %for o in objects :
    <% setLang(o.partner_id.lang) %>
  <div type="HEADER">
    <table width="718" cellpadding="2" cellspacing="0">
      <colgroup>
        <col width="127" />
      </colgroup>

      <colgroup>
        <col width="236" />
        <col width="178" />
      </colgroup>

      <colgroup>
        <col width="126" />
      </colgroup>


      <tr valign="top">
        <td colspan="2" width="367" class="c14">
          <p><spacer type="BLOCK" align="left" width="193" height="89" /><br /></p>
          <p><br /></p>
          <p><br /></p>

          <p class="c1">${o.company_id.partner_id.name or ''}</p>

          <p class="c2"><br /></p>

          <p class="c3">${o.company_id.partner_id.street or ''}
          ${o.company_id.partner_id.street2 or ''}</p>

          <p class="c4">${o.company_id.partner_id.zip or ''}
          ${o.company_id.partner_id.city or ''}</p>

          <p class="c8"><span class="c7"><span class=
          "c5">${_('Tel:')}</span> <span class=
          "c6">${o.company_id.partner_id.phone or ''}</span></span></p>

          <p class="c11"><span class="c9">${_('Fax:')}</span> <span class=
          "c10">${o.company_id.partner_id.fax or ''}</span></p>

          <p class="c8"><span class="c7"><span class=
          "c5">${_('Email:')}</span> <span class=
          "c6">${o.company_id.partner_id.email or ''}</span></span></p>

          <p class="c11"><span class="c9">${_('PIVA:')}</span> <span class=
          "c12">${o.company_id.partner_id.vat or ''}</span></p>

          <p class="c11"><span class="c9">${_('CF:')}</span> <span class=
          "c12">${o.company_id.partner_id.fiscalcode or ''}</span></p>

          <p class="c13"><br /></p>
        </td>

        <td colspan="2" width="343" class="c14">

          <table width="100%" cellpadding="11" cellspacing="0">
            <col width="256*" />

            <tr>
              <td width="100%" valign="top" class="c26">
                <p class="c4">${o.partner_id.name or ''}</p>

                <p class="c4"><br /></p>

                <p class="c3">${o.partner_id.street or ''}
                ${o.partner_id.street2 or ''}</p>

                <p class="c4">${o.company_id.partner_id.zip or ''}
                ${o.partner_id.city or ''}</p>

                <p class="c4"><br /></p>

                <p class="c18"><span class="c17"><b><span class="c16">${_('P.IVA')}</span></b><span class="c16">:</span>
                <span class="c16">${o.partner_id.vat or ''}</span></span></p>

                <p class="c22"><span class="c21"><tt><span class="c19">${_('TEL:')}</span></tt> <tt><span class=
                "c20">${o.partner_id.phone or ''}</span></tt></span></p>

                <p class="c22"><span class="c21"><tt><span class="c19">${_('FAX:')}</span></tt> <tt><span class=
                "c20">${o.partner_id.fax or ''}</span></tt></span></p>

                <p class="c4"><br /></p>

                <p class="c25"><span class="c24"><tt><span class="c20">${_('Cod. Cliente:')}</span></tt> <tt><span class=
                "c23">${o.partner_id.ref or ''}</span></tt></span></p>
              </td>
            </tr>
          </table>

          <p><br /></p>
        </td>
      </tr>

      <tr valign="top">
        <td width="127" height="49" class="c31">
          <p class="c28"><span class="c27">${_('N.&#176; documento')}</span></p>
          <p class="c30">${o.name or ''}</p>
        </td>

        <td width="236" class="c31">
          <p class="c28"><span class="c27">${_('Tipo')}</span></p>
          <p class="c32"><span class="c17">${_('Scheda di Lavoro')}</span></p>
        </td>

        <td width="178" class="c31">
          <p class="c28"><span class="c27">${_('Data emissione')}</span></p>
          <p class="c30">
          %if o.date_order:
              ${formatLang(o.date_order,date=True)}
          %else:
              ${''}
          %endif
          </p>
        </td>

        <td width="126" class="c37">
          <p class="c28"><span class="c27">${_('Ref. commerciale')}</span></p>
          <p class="c34">${o.user_id.name or ''}</p>
        </td>

      </tr>
    </table>

    <p class="c38"><br /></p>
  </div>

  <table width="100%" cellpadding="4" cellspacing="0" class="c46">
    <col width="37*" />
    <col width="156*" />
    <col width="27*" />
    <col width="36*" />

    <thead>
      <tr>
        <td width="14%" height="18" class="c41">
          <p class="c40"><span class="c39">${_('Cod. articolo')}</span></p>
        </td>

        <td width="61%" class="c41">
          <p class="c40"><span class="c39">${_('Descrizione')}</span></p>
        </td>

        <td width="11%" class="c41">
          <p class="c36"><span class="c39">${_('U.M.')}</span></p>
        </td>

        <td width="14%" class="c42">
          <p class="c36"><span class="c39">${_('Q.ta')}</span></p>
        </td>
      </tr>
    </thead>

    <tbody>

  %for line in o.order_line :

      <tr valign="top">
        <td width="14%" class="c43">
          <p class="c33">${line.product_id and line.product_id.code or ''}</p>
        </td>

        <td width="61%" class="c44">
          <p class="c33">
          %if line.product_id.type=='service':
            ${line.name or line.product_id.name or ''}
          %else:
            ${line.product_id.name or line.name or ''}
          %endif
          </p>
        </td>

        <td width="11%" class="c44">
          <p class="c45">${line.product_uom and line.product_uom.name or ''}</p>
        </td>

        <td width="14%" class="c44">
          <p class="c45">${formatLang(line.product_uom_qty) or 0.00}</p>
        </td>
      </tr>

  %endfor
    </tbody>
  </table>

  <p class="c38"><br /></p>
  <p class="c33"><br /></p>

  <div type="FOOTER">
    <table width="100%" cellpadding="4" cellspacing="0" class="c50">
      <col width="256*" />
      <tr>
        <td width="100%" height="55" valign="top" class="c49">
          <p class="c35"><span class="c47">${_('Note')}</span></p>
          <p class="c34">${o.note or ''}</p>
        </td>
      </tr>
    </table>

    <p style="margin-bottom: 0in; page-break-before: always"></p>
  </div>
  %endfor
</body>
</html>
