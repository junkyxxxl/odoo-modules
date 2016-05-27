# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
from openerp.osv import fields, orm
from openerp.tools.translate import _
from datetime import datetime
from string import digits


class invoice_file_export(orm.TransientModel):

    # FALSE = INCASSO DI FATTURE CLIENTI PER CASSA SE SI CONOSCE IL CODICE DEI CLIENTI
    # TRUE = INCASSO DI FATTURE CLIENTI PER CASSA SE NON SI CONOSCE IL CODICE DEI CLIENTI
    _CODE_CUSTOMER_FLAG = True

    _trfditta = "00001"
    _trfversione = "3"

    def _Recordfattura(self, value):
        t_str = ""
        line = t_str.join(value)
        return self._trfditta + self._trfversione + line + "\r\n"

    def _Recordopzionale(self, value):
        t_str = ""
        line = t_str.join(value)
        return self._trfditta + self._trfversione + line + "\r\n"

    def _Formatdate(self, date):
        date_temp = date.split('-')
        r_day = date_temp[2]
        r_month = date_temp[1]
        r_year = date_temp[0]
        registration_d = r_day+r_month+r_year
        return registration_d

    def _Formatnumber(self, number, size):
        if number < 0:
            result = str(format(abs(number), '.2f')).replace(".", "").rjust(size, "0")+"-"
        else:
            result = str(format(abs(number), '.2f')).replace(".", "").rjust(size, "0")+"+"
        return result

    def _TipoEffetti(self, type):

        res = ""
        if type == "C":
            res = "6"
        elif type == "B":
            res = "3"
        elif type == "D":
            res = "2"
        else:
            res = "5"

        return res

    def journaltype(self, journal_type):

        res = ""
        if journal_type == "sale":
            res = "Vendita"
        elif journal_type == "sale_refund":
            res = "Notacr:Vendita"
        elif journal_type == "purchase":
            res = "Acquisto"
        elif journal_type == "purchase_refund":
            res = "Notacr:acquisti"
        elif journal_type == "cash":
            res = "Contante"
        elif journal_type == "bank":
            res = "Banca e assegni"
        elif journal_type == "general":
            res = "generale"
        elif journal_type == "situation":
            res = "chiusura/apertu"

        return res

    def _creaFile(self, invoice):
        accumulatore = ""

        for value in invoice:
            accumulatore = accumulatore + self._Recordfattura(value[0])
            if value[1] != " ":
                accumulatore = accumulatore + self._Recordopzionale(value[1])
        return accumulatore

    def _get_ott_segu(self, cr, uid, obj_data, active_model, context):

        if active_model == "account.move" and self._CODE_CUSTOMER_FLAG:

            t_is_last = context.get('t_is_last', False)
            if t_is_last:
                return 'U'
            return 'S'

        return ''

    def _tab_alt_mov(self, cr, uid, obj_data, active_model, context):

        tab_alt_mov = ""
        conto = ""
        da = ""
        importo = ""
        cau_aggiunt = ""
        ec_partita_pag = ""
        ec_partita_anno_pag = ""
        ec_imp_val = ""
        filler = ""

        if active_model == "account.move" and self._CODE_CUSTOMER_FLAG:
            # tabella altri movimenti
            if obj_data:
                t_line_list = context.get('t_line_list', [])
                for line in obj_data.line_id:
                    if line.id in t_line_list:
                        conto = line.account_id.code
                        if line.debit > 0:
                            da = "D"
                            importo = self._Formatnumber(line.debit, 11)
                        else:
                            conto = "9999999"
                            da = "A"
                            importo = self._Formatnumber(line.credit, 11)
                        tab_alt_mov = tab_alt_mov + conto.rjust(7, "0") + da.ljust(1, " ") + importo.rjust(11,"0")+cau_aggiunt.ljust(18," ")+ec_partita_pag.rjust(6,"0")+ec_partita_anno_pag.rjust(4,"0")+ec_imp_val.rjust(15,"0")+"+"
                # riempimento
                len_fill = 80 - len(t_line_list)

                if len_fill > 0 and len_fill < 80:

                    for index in range(len_fill):
                        tab_alt_mov = tab_alt_mov + filler.rjust(7, "0") + filler.ljust(1, " ") + filler.rjust(11,"0")+"+"+filler.ljust(18," ")+filler.rjust(6,"0")+filler.rjust(4,"0")+filler.rjust(15,"0")+"+"  

                else:
                    raise orm.except_orm('Error', _('Righe fatture superiori ad 8'))

            else:
                for index in range(80):
                    tab_alt_mov = tab_alt_mov+conto.rjust(7,"0") + da.ljust(1," ") + importo.rjust(11,"0")+"+"+cau_aggiunt.ljust(18," ")+ec_partita_pag.rjust(6,"0")+ec_partita_anno_pag.rjust(4,"0")+ec_imp_val.rjust(15,"0")+"+"  
        elif active_model == "account.move":
            # tabella altri movimenti
            if obj_data:
                for line in obj_data.line_id:
                    conto = line.account_id.code
                    if line.debit > 0:
                        da = "D"
                        importo = self._Formatnumber(line.debit, 11)
                    else:
                        da = "A"
                        importo = self._Formatnumber(line.credit, 11)
                    tab_alt_mov = tab_alt_mov + conto.rjust(7, "0") + da.ljust(1, " ") + importo.rjust(11,"0")+cau_aggiunt.ljust(18," ")+ec_partita_pag.rjust(6,"0")+ec_partita_anno_pag.rjust(4,"0")+ec_imp_val.rjust(15,"0")+"+"
                # riempimento
                len_fill = 80 - len(obj_data.line_id)

                if len_fill > 0 and len_fill < 80:

                    for index in range(len_fill):
                        tab_alt_mov = tab_alt_mov + filler.rjust(7, "0") + filler.ljust(1, " ") + filler.rjust(11,"0")+"+"+filler.ljust(18," ")+filler.rjust(6,"0")+filler.rjust(4,"0")+filler.rjust(15,"0")+"+"  

                else:
                    raise orm.except_orm('Error', _('Righe fatture superiori ad 8'))

            else:
                for index in range(80):
                    tab_alt_mov = tab_alt_mov+conto.rjust(7,"0") + da.ljust(1," ") + importo.rjust(11,"0")+"+"+cau_aggiunt.ljust(18," ")+ec_partita_pag.rjust(6,"0")+ec_partita_anno_pag.rjust(4,"0")+ec_imp_val.rjust(15,"0")+"+"  
        else:
            for index in range(80):
                tab_alt_mov = tab_alt_mov+conto.rjust(7,"0") + da.ljust(1," ") + importo.rjust(11,"0") + "+"+cau_aggiunt.ljust(18," ")+ec_partita_pag.rjust(6,"0")+ec_partita_anno_pag.rjust(4,"0")+ec_imp_val.rjust(15,"0")+"+"  

        return tab_alt_mov

    def _ricavocosto(self, invoice, context):

        cdrcosto = ""
        if context == "account.invoice":
            Lista_conti = []
            for line in invoice.invoice_line:
                Id = line.account_id.code
                Var_id = str(Id)
                if Id not in Lista_conti:
                    Lista_conti.append(Id)
                    locals()[Var_id] = line.price_subtotal
                else:
                    locals()[Var_id] = locals()[Var_id] + line.price_subtotal
            for line in Lista_conti:
                cdrcosto = cdrcosto + str(line).rjust(7, "0")
                cdrcosto = cdrcosto+self._Formatnumber(locals()[line], 11)

            # riempimento di conti di ricavo costo
            len_fill = 8 - len(Lista_conti)

            if len_fill > 0 and len_fill < 9:

                for index in range(len_fill):
                    cdrcosto = cdrcosto + "000000000000000000+"

            else:
                raise orm.except_orm('Error', _('Righe conti ricavo costo superiori ad 8'))

        else:
            for index in range(8):
                cdrcosto = cdrcosto + "000000000000000000+"

        return cdrcosto

    def _export_ivoicedata(self, invoice, context):

        cause = ""
        description = ""
        additional_description1 = ""
        additional_description2 = ""
        additional_description3 = ""
        registration_d = ""
        document_date = ""
        ndoc = ""
        num_doc_for = ""
        sezionaleiva = ""
        ec_partita = ""
        ec_partita_anno = ""
        ec_cod_val = ""
        ec_cambio = ""
        ec_data_cambio = ""
        ec_tot_doc_val = ""
        ec_tot_iva_val = ""
        plafond = ""

        if context == "account.invoice":

            # data di registrazione
            if not invoice.registration_date:
                registration_d = ""
            else:
                registration_d = self._Formatdate(invoice.registration_date)

            # data del documento
            if not invoice.date_invoice:
                document_date = ""
            else:
                document_date = self._Formatdate(invoice.date_invoice)
            # fattura cliente
            if invoice.type == "out_invoice":
                cause = "001"
                description = "Fatt Vendita"
                array_temp = str(invoice.number).split("/")
                size = len(array_temp)
                ndoc = array_temp[size-1]
            # nota di credito cliente
            elif invoice.type == "out_refund":
                cause = "012"
                description = "Nota di Credito"
                additional_description2 = "Cliente"
                array_temp = str(invoice.number).split("/")
                size = len(array_temp)
                ndoc = array_temp[size-1]
            # ǹota di credito fornitore
            elif invoice.type == "in_refund":
                cause = "012"
                description = "Nota di Credito"
                additional_description2 = "Fornitore"
                array_temp = str(invoice.number).split("/")
                size = len(array_temp)
                ndoc = array_temp[size-1]

            # fattura acquisto
            elif invoice.type == "in_invoice":
                cause = "011"
                description = "Fatt Acquisto"

                if not invoice.supplier_invoice_number:
                    ndoc = ""
                else:
                    temp_ndoc = str(invoice.supplier_invoice_number).replace("/", "")
                    if len(temp_ndoc) < 6:
                        ndoc = temp_ndoc
                    else:
                        sizef = len(temp_ndoc)
                        sizes = sizef-5
                        ndoc = temp_ndoc[sizes:sizef]

            # altro
            else:
                cause = "020"

        elif context == "account.move":

            cause = "027"
            description = self.journaltype(invoice.journal_id.type)
            # data di registrazione
            if invoice.date:
                registration_d = self._Formatdate(invoice.date)

            # data del documento
            if invoice.document_date:
                document_date = self._Formatdate(invoice.document_date)

        if ndoc:
            ndoc = ''.join(c for c in ndoc if c in digits)

        data_invoice=[cause,description,additional_description1,additional_description2,additional_description3,registration_d,document_date,ndoc,num_doc_for,sezionaleiva,ec_partita,ec_partita_anno,ec_cod_val,ec_cambio,ec_data_cambio,ec_tot_doc_val,ec_tot_iva_val,plafond]
        return data_invoice

    def _extract_dativa(self, invoice, active_model, cr, uid):
        # metodo per l'estrazione dei dati che vanno a popolare la tabella dati iva
        # per una data fattura tramite la chiave di riferimento tax_line legge
        # da account.invoice.tax le linee fattura associata al movimento (invoice)
        # dalla tabella account.invoice.tax estrae imponibile e imposta,
        # da invoice il totale fattura, mentre per l'aliquota viene presa da account.tax

        dati_iva = ""
        filler = ""
        tot_fat = ""

        if active_model == "account.invoice":

            for line in invoice.tax_line:
                imponibile = self._Formatnumber(abs(line.base_amount), 11)

                # codice aliquota
                aliq = line.tax_code_id and line.tax_code_id.gamma_code or ""

                # fine ricerca aliquota
                aliq_agricola = ""
                iva11 = ""
                imposta = self._Formatnumber(line.amount, 10)
                dati_iva = dati_iva + imponibile + aliq.rjust(3, "0") + aliq_agricola.rjust(3, "0") + iva11.rjust(2, "0") + imposta

            # riempimento
            len_fill = 8 - len(invoice.tax_line)

            if len_fill > 0 and len_fill < 9:

                for t_index in range(len_fill):
                    dati_iva = dati_iva+filler.rjust(11, "0") + "+" + filler.rjust(3,"0") + filler.rjust(3, "0") + filler.rjust(2, "0") + filler.rjust(10, "0") + "+"

            else:
                raise orm.except_orm('Error', _('Righe fatture superiori ad 8'))

            if invoice.amount_total:
                tot_fat = self._Formatnumber(invoice.amount_total, 11)

        else:
            for t_index in range(8):
                dati_iva = dati_iva+filler.rjust(11, "0") + "+"+filler.rjust(3, "0") + filler.rjust(3, "0") + filler.rjust(2,"0")+filler.rjust(10,"0")+"+"

        return [dati_iva, tot_fat]

    def _extract_personaldata(self, obj_data, active_model, context):

        partner = None

        fcodclifor = ""
        full_name = ""
        street_partner = ""
        cap = ""
        city_partner = ""
        province_cod = ""
        fiscal_code = ""
        piva = ""
        pf = ""
        blank = ""
        ecountrycode = ""
        efiscalcode = ""
        epiva = ""
        sex = ""
        birth_date = ""
        birth_city = ""
        birth_province = ""
        phone = ""
        fax_number = ""
        cdca_code = ""
        cp_code = ""
        abi_code = ""
        cab_code = ""
        intermediate_code = ""

        if active_model == "account.invoice":
            partner = obj_data.partner_id
        elif active_model == "res.partner":
            partner = obj_data
        elif active_model == "account.move" and self._CODE_CUSTOMER_FLAG:
            if obj_data:
                t_partner_id = context.get('t_partner_id', None)
                if t_partner_id:
                    for t_line in obj_data.line_id:
                        if t_line.partner_id and t_line.partner_id.id == t_partner_id:
                            partner = t_line.partner_id

        if partner:
            # iva
            if partner.vat:
                piva = partner.vat[2:13]

            if partner.is_company:
                full_name = partner.name

            else:
                if not partner.person_name and not partner.person_surname:
                    full_name = partner.name
                else:
                    if partner.person_name:
                        name_partner = partner.person_name

                    if partner.person_surname:
                        surname_partner = partner.person_surname
                        blank = str(len(surname_partner)+1)

                    full_name = surname_partner + " " + name_partner

                    if partner.birth_date:
                        str_data = self._Formatdate(partner.birth_date)

                    if partner.birth_city_id and partner.birth_city_id.name:
                        birth_city = partner.birth_city_id.name

                    if partner.birth_city_id and partner.birth_city_id.province_id:
                        birth_province = partner.birth_city_id.province_id.code

            fiscal_code = piva
            if partner.fiscalcode:
                fiscal_code = partner.fiscalcode

            if not partner.street and not partner.street2:
                street_partner = ''
            elif partner.street and not partner.street2:
                street_partner = partner.street
                street_partner = street_partner.encode('ascii', 'replace')
            elif not partner.street and partner.street2:
                street_partner = partner.street2
                street_partner = street_partner.encode('ascii', 'replace')
            else:
                street_partner = partner.street + partner.street2
                street_partner = street_partner.encode('ascii', 'replace')

            if partner.city:
                city_partner = partner.city  # TRF-CITTA

            if partner.zip:
                cap = str(partner.zip)[0:5]  # TRF-CAP

            if partner.province.code:
                province_cod = partner.province.code

            if partner.sex:
                sex = partner.sex

            individual = partner.individual

            pf = "N"
            if individual:
                pf = "S"

            if not partner.phone:
                phone = ""
                if partner.mobile:
                    phone = partner.mobile
            else:
                phone = partner.phone

        personaldata = [fcodclifor,
                        full_name,
                        street_partner,
                        cap,
                        city_partner,
                        province_cod,
                        fiscal_code,
                        piva,
                        pf,
                        blank,
                        ecountrycode,
                        efiscalcode,
                        epiva,
                        sex,
                        birth_date,
                        birth_city,
                        birth_province,
                        phone,
                        fax_number,
                        cdca_code,
                        cp_code,
                        abi_code,
                        cab_code,
                        intermediate_code
                        ]
        return personaldata

    def _extract_ratei(self, invoice):
        tab_rat_risc = ""

        for index in range(10):
            rifer_tab = ""
            ind_riga = ""
            dt_ini = ""
            dt_fin = ""
            tab_rat_risc = tab_rat_risc+rifer_tab.ljust(1, " ") + ind_riga.rjust(2, "0") + dt_ini.ljust(8, " ") + dt_fin.ljust(8, " ")

        return tab_rat_risc

    def _otherpaymentmov(self, invoice):

        tab_utl_dat_alt_mov = ""
        for index in range(80):
            ec_pratica_sez_pag = ""
            tab_utl_dat_alt_mov = tab_utl_dat_alt_mov + ec_pratica_sez_pag.rjust(2, "0")
        return tab_utl_dat_alt_mov

    def _otherunitmov(self, invoice):

        tab_dat_un_prod_ric = ""
        for index in range(8):
            unita_ricavi = ""
            tab_dat_un_prod_ric = tab_dat_un_prod_ric + unita_ricavi.rjust(2, "0")

        return tab_dat_un_prod_ric

    def _otherunitpaymentmov(self, invoice):

        tab_dat_un_prod_pag = ""
        for index in range(80):
            unita_pagam = ""
            tab_dat_un_prod_pag = tab_dat_un_prod_pag + unita_pagam.rjust(2, "0")
        return tab_dat_un_prod_pag

    def _ivaeditoria(self, invoice):

        tab_editoria = ""
        for index in range(8):
            perc_forf = ""
            tab_editoria = tab_editoria + perc_forf.rjust(3, "0")
        return tab_editoria

    def _intrastat(self):

        tab_mov_intrastat = ""
        for index in range(20):
            nomenclatura = ""
            imp_lire = ""
            imp_val = ""
            natura = ""
            massa = ""
            un_suppl = ""
            val_stat = ""
            regime = ""
            trasporto = ""
            paese_prov = ""
            paese_orig = ""
            paese_dest = ""
            prov_dest = ""
            prov_orig = ""
            segno_ret = ""
            tab_mov_intrastat = tab_mov_intrastat + nomenclatura.ljust(8, " ") + imp_lire.rjust(12, "0") + imp_val.rjust(12, "0") + natura.ljust(1, " ") + massa.rjust(12, "0") + un_suppl.rjust(12, "0") + val_stat.rjust(12, "0") + regime.ljust(1, " ") + trasporto.ljust(1, " ") + paese_prov.rjust(3, "0") + paese_orig.rjust(3, "0") + paese_dest.rjust(3, "0") + prov_dest.ljust(2, " ") + prov_orig.ljust(2, " ") + segno_ret.ljust(1, " ")

        return tab_mov_intrastat

    def _ritenuta_dacconto(self, invoice, context):

        rita_tipo = ""
        rita_impon = ""
        rita_aliq = ""
        rita_impra = ""

        if context == "account.invoice":
            # ritenuta d’acconto
            if invoice.partner_id.wht_account_id:

                rita_cod_temp = invoice.partner_id.wht_account_id.name

                # prestazioni
                if rita_cod_temp == "1040" or rita_cod_temp == "1043":
                    rita_tipo = "1"
                    rita_impon = self._Formatnumber(invoice.amount_untaxed, 10)
                    rita_aliq = str(invoice.partner_id.wht_account_id.wht_tax_rate).replace(".", "0")
                    rita_impra = self._Formatnumber(invoice.wht_amount, 9)
                # provvigioni
                else:
                    rita_tipo = "2"
                    rita_impon = str(invoice.amount_untaxed)
                    rita_aliq = str(invoice.partner_id.wht_account_id.wht_tax_rate).replace(".", "0")
                    rita_impra = self._Formatnumber(invoice.wht_amount, 9)

            # se la ritenuta non è presente

        return [rita_tipo, rita_impon, rita_aliq, rita_impra]

    def _detaileffects(self, invoice, cr, uid, context):

        por_tot_rate = ""
        tab_det_eff = ""
        por_totdoc = ""
        if context == "account.invoice":

            por_totdoc = self._Formatnumber(invoice.amount_total, 11)
            obj_pt = self.pool.get('account.payment.term')

            t_amount_total = invoice.amount_total
            pterm_list = []
            if invoice.payment_term:
                pterm_list = obj_pt.compute(cr, uid, invoice.payment_term.id,
                                            t_amount_total,
                                            date_ref=invoice.date_invoice)

            if pterm_list:
                por_tot_rate = str(len(pterm_list))
                por_num_rata = 0
                for line in pterm_list:
                    por_num_rata = por_num_rata+1
                    por_datascad = self._Formatdate(line[0])
                    por_tipoeff = self._TipoEffetti(line[2])
                    por_importo_eff = self._Formatnumber(line[1], 11)
                    por_importo_effval = ""
                    por_importo_bolli = ""
                    por_importo_bolival = ""
                    por_flag = ""
                    por_tipo_rd = ""
                    tab_det_eff = tab_det_eff+str(por_num_rata).rjust(2,"0")+por_datascad.rjust(8,"0")+por_tipoeff.rjust(1,"0")+por_importo_eff+por_importo_effval.rjust(14,"0")+"+"+por_importo_bolli.rjust(11,"0")+"+"+por_importo_bolival.rjust(14,"0")+"+"+por_flag.ljust(1,"0")+por_tipo_rd.ljust(1," ")

                # riempimento di conti di ricavo costo
                len_fill = 12 - len(pterm_list)

                if len_fill > 0 and len_fill < 13:
                    for index in range(len_fill):
                        tab_det_eff = tab_det_eff + "0000000000000000000000+00000000000000+00000000000+00000000000000+0 "

                else:
                    raise orm.except_orm('Error', _('Righe superiori a 12 '))

            else:
                por_tot_rate = "1"
                por_num_rata = "1"
                por_datascad = self._Formatdate(invoice.date_invoice)
                por_tipoeff = ""
                por_importo_eff = self._Formatnumber(invoice.amount_total, 11)
                por_importo_effval = ""
                por_importo_bolli = ""
                por_importo_bolival = ""
                por_flag = ""
                por_tipo_rd = ""
                tab_det_eff = tab_det_eff+por_num_rata.rjust(2,"0")+por_datascad.rjust(8,"0")+por_tipoeff.rjust(1,"0")+por_importo_eff+por_importo_effval.rjust(15,"0")+por_importo_bolli.rjust(12,"0")+por_importo_bolival.rjust(15,"0")+por_flag.ljust(1," ")+por_tipo_rd.ljust(1," ")  

                for index in range(11):
                    por_num_rata = ""
                    por_datascad = ""
                    por_tipoeff = ""
                    por_importo_eff = ""
                    por_importo_effval = ""
                    por_importo_bolli = ""
                    por_importo_bolival = ""
                    por_flag = ""
                    por_tipo_rd = ""
                    tab_det_eff = tab_det_eff+por_num_rata.rjust(2,"0")+por_datascad.rjust(8,"0")+por_tipoeff.rjust(1,"0")+por_importo_eff.rjust(12,"0")+por_importo_effval.rjust(15,"0")+por_importo_bolli.rjust(12,"0")+por_importo_bolival.rjust(15,"0")+por_flag.ljust(1," ")+por_tipo_rd.ljust(1," ")

        else:
            for index in range(11):
                por_num_rata = ""
                por_datascad = ""
                por_tipoeff = ""
                por_importo_eff = ""
                por_importo_effval = ""
                por_importo_bolli = ""
                por_importo_bolival = ""
                por_flag = ""
                por_tipo_rd = ""
                tab_det_eff = tab_det_eff+por_num_rata.rjust(2,"0")+por_datascad.rjust(8,"0")+por_tipoeff.rjust(1,"0")+por_importo_eff.rjust(12,"0")+por_importo_effval.rjust(15,"0")+por_importo_bolli.rjust(12,"0")+por_importo_bolival.rjust(15,"0")+por_flag.ljust(1," ")+por_tipo_rd.ljust(1," ")

        return [por_tot_rate, tab_det_eff, por_totdoc]

    def _interstatmov(self):

        tabella_mov_interstat_ben = ""
        for index in range(20):
            cod_val_iv = ""
            imp_valuta_iv = ""
            tabella_mov_interstat_ben=tabella_mov_interstat_ben+cod_val_iv.rjust(3," ")+imp_valuta_iv.rjust(16,"0")   
        return tabella_mov_interstat_ben

    def _interstatservice(self): 

        tab_mov_interstat_servizi = ""
        for index in range(20):
            codice_servizio = ""
            stato_pagamento = ""
            serv_imp_euro = ""
            serv_imp_val = ""
            data_doc_orig = ""
            mod_erogazione = ""
            mod_incasso = ""
            prot_reg = ""
            prog_reg = ""
            cod_sez_dog_ret = ""
            anno_reg_ret = ""
            num_doc_orig = ""
            serv_segno_ret = ""
            serv_cod_val_iv = ""
            serv_imp_valuta_iv = ""
            tab_mov_interstat_servizi=tab_mov_interstat_servizi+codice_servizio.ljust(6," ")+stato_pagamento.rjust(3,"0")+serv_imp_euro.rjust(12,"0")+serv_imp_val.rjust(12,"0")+data_doc_orig.rjust(8,"0")+mod_erogazione.ljust(1," ")+mod_incasso.ljust(1," ")+prot_reg.rjust(6,"0")+prog_reg.rjust(6,"0")+cod_sez_dog_ret.rjust(6,"0")+anno_reg_ret.rjust(2,"0")+num_doc_orig.ljust(15," ")+serv_segno_ret.ljust(1," ")+serv_cod_val_iv.ljust(3," ")+serv_imp_valuta_iv.ljust(16," ")

        return tab_mov_interstat_servizi

    def _checkiva(self):
        tab_check_iva = ""
        for index in range(8):
            ck_rcharge = ""
            tab_check_iva = tab_check_iva + ck_rcharge.ljust(1, " ")

        return tab_check_iva

    def _layoutrecord(self, order_obj, active_model, cr, uid, context):

        tarc = "0"
        # DATI CLIENTE / FORNITORE
        [fcodclifor,full_name,street_partner,cap,city_partner,province_cod,fiscal_code,piva,pf,blank,ecountrycode,efiscalcode,epiva,sex,birth_date,birth_city,birth_province,phone,fax_number,cdca_code,cp_code,abi_code,cab_code,intermediate_code]=self._extract_personaldata(order_obj, active_model, context)
        # Dati Fattura
        [cause,description,additional_description1,additional_description2,additional_description3,registration_d,document_date,ndoc,num_doc_for,sezionaleiva,ec_partita,ec_partita_anno,ec_cod_val,ec_cambio,ec_data_cambio,ec_tot_doc_val,ec_tot_iva_val,plafond]=self._export_ivoicedata(order_obj, active_model)
        # DATI-IVA massimo 8 voci, ciascuno di size 31
        [dati_iva, tot_fat] = self._extract_dativa(order_obj, active_model, cr, uid)
        # Conti di ricavo costo
        cdrcosto = self._ricavocosto(order_obj, active_model)
        # Dati eventuale pagamento fattura o movimenti diversi
        cau_pagam = ''
        cau_des_pagam = ''
        cau_agg_1_pagam = ''
        cau_agg_2_pagam = ''
        ott_segu = self._get_ott_segu(cr, uid, order_obj, active_model, context)
        # tabella altri movimenti
        tab_alt_mov = self._tab_alt_mov(cr, uid, order_obj, active_model, context)
        # tabella ratei e riscontri
        tab_rat_risc = self._extract_ratei(order_obj)
        doc = ''
        # Ulteriori dati cliente fornitore
        an_omonimi = ''
        an_tipo_sogg = ""
        # Ulteriori dati eventuale pagamento fattura o movimenti diversi
        tab_utl_dat_alt_mov = self._otherpaymentmov(order_obj)
        # Ulteriori dati gestione professionista per eventuale pagamento incasso fattura o dati fattura
        num_doc_pag_prof = ''
        data_doc_pag_prof = ''
        rit_acc = ''
        rit_prev = ''
        rit_1 = ''
        rit_2 = ''
        rit_3 = ''
        rit_4 = ''
        # Ulteriori dati per unità produttive ricavi
        tab_dat_un_prod_ric = self._otherunitmov(order_obj)
        # Ulteriori dati per unita’ produttive pagamenti
        tab_dat_un_prod_pag = self._otherunitpaymentmov(order_obj)
        # Ulteriori dati cliente fornitore
        fax_pref = ''
        fax_num = ''

        # TODO da modificare, soggetta a bug ?
        solo_clifor = ''
        if active_model == "res.partner":
            if order_obj.customer:
                solo_clifor = "C"
            else:
                solo_clifor = "F"

        # Ulteriori dati gestione professionista per eventuale incasso/ pagamento fattura o dati fattura
        conto_rit_acc = ''
        conto_rit_prev = ''
        conto_rit_1 = ''
        conto_rit_2 = ''
        conto_rit_3 = ''
        conto_rit_4 = ''
        # Varie
        differimento_iva = ''
        storico = ''
        storico_data = ''
        caus_ori = ''
        # Prima nota previsionale dati aggiuntivi
        prev_tipomov = ''
        prev_ratris = ''
        prev_dtcomp_ini = ''
        prev_dtcomp_fin = ''
        prev_flag_cont = ''
        # Varie
        riferimento = ''
        caus_prest_ana = ''
        ec_tipo_paga = ''
        conto_iva_ven_acq = ''
        piva_vecchia = ''
        piva_estero_vecchia = ''
        riservato = ''
        data_iva_agviaggi = ''
        dati_agg_ana_rec4 = ''
        rif_iva_note_cred = ''
        rif_iva_anno_prec = ''
        natura_giuridica = ''
        stampa_elenco = ''
        # Iva Editoria
        tab_editoria = self._ivaeditoria(order_obj)
        solo_mov_iva = ''
        cofi_vecchio = ''
        usa_piva_vecchia = ''
        usa_piva_est_vecchia = ''
        usa_cofi_vecchio = ''
        esigibilita_iva = ''
        tipo_mov_risconti = ''
        aggiorna_ec = ''
        blacklist_anag = ''
        blacklist_iva = ''
        blacklist_iva_ana = ''
        contea_estero = ''
        art21_anag = ''
        art21_iva = ''
        rif_fattura = ''
        riservato_b = ''
        filler = ''

        fattura = [tarc.rjust(1, "0")[-1:],
                   fcodclifor.rjust(5, "0")[-5:],
                   full_name.ljust(32, " ")[-32:],
                   street_partner.ljust(30, " ")[-30:],
                   cap.rjust(5, " ")[-5:],
                   city_partner.ljust(25, " ")[-25:],
                   province_cod.ljust(2, " ")[-2:],
                   fiscal_code.ljust(16, " ")[-16:],
                   piva.rjust(11, " ")[-11:],
                   pf.ljust(1, " ")[-1:],
                   blank.rjust(2, "0")[-2:],
                   ecountrycode.rjust(4, "0")[-4:],
                   efiscalcode.rjust(12, " ")[-12:],
                   epiva.rjust(20, " ")[-20:],
                   sex.ljust(1, " ")[-1:],
                   birth_date.rjust(8, " ")[-8:],
                   birth_city.ljust(25, " ")[-25:],
                   birth_province.ljust(2, " ")[-2:],
                   phone.ljust(24, " ")[-24:],
                   fax_number.ljust(13, " ")[-13:],
                   cdca_code.rjust(7, "0")[-7:],
                   cp_code.rjust(4, "0")[-4:],
                   abi_code.rjust(5, "0")[-5:],
                   cab_code.rjust(5, "0")[-5:],
                   intermediate_code.rjust(1, "0")[-1:],
                   cause.rjust(3, "0")[-3:],
                   description.ljust(15, " ")[-15:],
                   additional_description1.ljust(18, " ")[-18:],
                   additional_description2.ljust(34, " ")[-34:],
                   additional_description3.ljust(34, " ")[-34:],
                   registration_d.rjust(8, "0")[-8:],
                   document_date.rjust(8, "0")[-8:],
                   num_doc_for.rjust(8, "0")[-8:],
                   ndoc.rjust(5, "0")[-5:],
                   sezionaleiva.rjust(2, "0")[-2:],
                   ec_partita.rjust(6, "0")[-6:],
                   ec_partita_anno.rjust(4, "0")[-4:],
                   ec_cod_val.rjust(3, "0")[-3:],
                   ec_cambio.rjust(12, "0")[-12:]+"+",
                   ec_data_cambio.rjust(8, " ")[-8:],
                   ec_tot_doc_val.rjust(15, "0")[-15:]+"+",
                   ec_tot_iva_val.rjust(15, "0")[-15:]+"+",
                   plafond.rjust(6, "0")[-6:],
                   dati_iva,
                   tot_fat.rjust(12, "0")[-12:],
                   cdrcosto,
                   cau_pagam.rjust(3, "0")[-3:],
                   cau_des_pagam.ljust(15, " ")[-15:],
                   cau_agg_1_pagam.ljust(34, " ")[-34:],
                   cau_agg_2_pagam.ljust(34, " ")[-34:],
                   tab_alt_mov,
                   tab_rat_risc,
                   doc.rjust(6, "0")[-6:],
                   an_omonimi.ljust(1, " ")[-1:],
                   an_tipo_sogg.rjust(1, "0")[-1:],
                   tab_utl_dat_alt_mov,
                   num_doc_pag_prof.rjust(7, "0")[-7:],
                   data_doc_pag_prof.ljust(8, " ")[-8:],
                   rit_acc.rjust(12, "0")[-12:],
                   rit_prev.rjust(12, "0")[-12:],
                   rit_1.rjust(12, "0")[-12:],
                   rit_2.rjust(12, "0")[-12:],
                   rit_3.rjust(12, "0")[-12:],
                   rit_4.rjust(12, "0")[-12:],
                   tab_dat_un_prod_ric,
                   tab_dat_un_prod_pag,
                   fax_pref.ljust(4, " ")[-4:],
                   fax_num.ljust(20, " ")[-20:],
                   solo_clifor.ljust(1, " ")[-1:],
                   ott_segu.ljust(1, " ")[-1:],
                   conto_rit_acc.rjust(7, "0")[-7:],
                   conto_rit_prev.rjust(7, "0")[-7:],
                   conto_rit_1.rjust(7, "0")[-7:],
                   conto_rit_2.rjust(7, "0")[-7:],
                   conto_rit_3.rjust(7, "0")[-7:],
                   conto_rit_4.rjust(7, "0")[-7:],
                   differimento_iva.ljust(1, " ")[-1:],
                   storico.ljust(1, " ")[-1:],
                   storico_data.ljust(8, " ")[-8:],
                   caus_ori.rjust(3, "0")[-3:],
                   prev_tipomov.ljust(1, " ")[-1:],
                   prev_ratris.ljust(1, " ")[-1:],
                   prev_dtcomp_ini.ljust(8, " ")[-8:],
                   prev_dtcomp_fin.ljust(8, " ")[-8:],
                   prev_flag_cont.ljust(1, " ")[-1:],
                   riferimento.ljust(20, " ")[-20:],
                   caus_prest_ana.rjust(2, "0")[-20:],
                   ec_tipo_paga.rjust(1, "0")[-1:],
                   conto_iva_ven_acq.rjust(7, "0")[-7:],
                   piva_vecchia.rjust(11, "0")[-11:],
                   piva_estero_vecchia.ljust(12, " ")[-12:],
                   riservato.ljust(32, " ")[-32:],
                   data_iva_agviaggi.ljust(8, " ")[-8:],
                   dati_agg_ana_rec4.ljust(1, " ")[-1:],
                   rif_iva_note_cred.ljust(6, "0")[-6:],
                   rif_iva_anno_prec.ljust(1, " ")[-1:],
                   natura_giuridica.rjust(2, "0")[-2:],
                   stampa_elenco.ljust(1, " ")[-1:],
                   tab_editoria,
                   solo_mov_iva.ljust(1, " ")[-1:],
                   cofi_vecchio.ljust(16, " ")[-16:],
                   usa_piva_vecchia.ljust(1, " ")[-1:],
                   usa_piva_est_vecchia.ljust(1, " ")[-1:],
                   usa_cofi_vecchio.ljust(1, " ")[-1:],
                   esigibilita_iva.rjust(1, "0")[-1:],
                   tipo_mov_risconti.ljust(1, " ")[-1:],
                   aggiorna_ec.ljust(1, " ")[-1:],
                   blacklist_anag.ljust(1, " ")[-1:],
                   blacklist_iva.ljust(1, " ")[-1:],
                   blacklist_iva_ana.rjust(6, "0")[-6:],
                   contea_estero.ljust(20, " ")[-20:],
                   art21_anag.ljust(1, " ")[-1:],
                   art21_iva.ljust(1, " ")[-1:],
                   rif_fattura.ljust(1, " ")[-1:],
                   riservato_b.ljust(1, " ")[-1:],
                   filler.ljust(3, "f")[-3:],
                   filler.ljust(2, "f")[-2:],
                   ]

        return fattura

    def _optionalrecord(self, order_obj, active_model, cr, uid):

        filler = ''
        # RECORD OPZIONALE opzionale contenente dati aggiuntivi della contabile ovvero
        # ritenute d’acconto, modello INTRASTAT, e portafoglio effetti
        tarc_op = ''
        # dati intrastat
        num_autofatt = ''
        serie_autofatt = ''
        cod_val = ''
        totval = ''
        # movimenti intrastat beni
        tab_mov_intrastat = self._intrastat()
        intra_tipo = ''
        mese_anno_rif = ''
        [rita_tipo, rita_impon, rita_aliq, rita_impra] = self._ritenuta_dacconto(order_obj, active_model)
        rita_prons = ''
        rita_mese = ''
        rita_causa = ''
        rita_tribu = ''
        rita_dtvers = ''
        rita_impag = ''
        rita_tpag = ''
        rita_serie = ''
        rita_quietanza = ''
        rita_num_boll = ''
        rita_abi = ''
        rita_cab = ''
        rita_aacomp = ''
        rita_cred = ''
        # dati contributo inps e modello gla/d
        rita_sogg = ''
        rita_baseimp = ''
        rita_franchigia = ''
        rita_cto_perc = ''
        rita_cto_ditt = ''
        rita_data = ''
        rita_totdoc = ''
        rita_impvers = ''
        rita_data_i = ''
        rita_data_f = ''
        emens_att = ''
        emens_rap = ''
        emens_ass = ''
        # dati portafoglio
        por_codpag = ''
        por_banca = ''
        por_agenzia = ''
        por_desagenzia = ''
        # dettaglio effetti
        [por_tot_rate, tab_det_eff, por_totdoc] = self._detaileffects(order_obj, cr, uid, active_model)
        por_codage = ''
        por_effetto_sosp = ''
        # movimenti intrastat beni dati aggiuntivi
        tabella_mov_interstat_ben = self._interstatmov()
        # movimenti intrastat servizi
        tab_mov_interstat_servizi = self._interstatservice()
        intra_tipo_servizio = ''
        serv_mese_anno_rif = ''
        # check iva reverse charge
        tab_check_iva = self._checkiva()
        xnum_doc_ori = ''

        record_opzione = [tarc_op.rjust(1, "1")[-1:],
                          num_autofatt.rjust(5, "0")[-5:],
                          serie_autofatt.rjust(2, "0")[-2:],
                          cod_val.ljust(3, " ")[-3:],
                          totval.rjust(14, "0")[-14:],
                          tab_mov_intrastat,
                          intra_tipo.ljust(1, " ")[-1:],
                          mese_anno_rif.rjust(6, " ")[-6:],
                          filler.ljust(173, " ")[-173:],
                          rita_tipo.rjust(1, "0")[-1:],
                          rita_impon.rjust(11, "0")[-11:],
                          rita_aliq.rjust(4, "0")[-4:],
                          rita_impra.rjust(10, "0")[-10:],
                          rita_prons.rjust(11, "0")[-11:],
                          rita_mese.rjust(6, "0")[-6:],
                          rita_causa.rjust(2, "0")[-2:],
                          rita_tribu.rjust(4, "0")[-4:],
                          rita_dtvers.rjust(8, "0")[-8:],
                          rita_impag.rjust(11, "0")[-11:],
                          rita_tpag.rjust(1, "0")[-1:],
                          rita_serie.ljust(4, " ")[-4:],
                          rita_quietanza.ljust(12, " ")[-12:],
                          rita_num_boll.ljust(12, " ")[-12:],
                          rita_abi.rjust(5, "0")[-5:],
                          rita_cab.rjust(5, "0")[-5:],
                          rita_aacomp.rjust(4, "0")[-4:],
                          rita_cred.rjust(11, "0")[-11:],
                          rita_sogg.ljust(1, " ")[-1:],
                          rita_baseimp.rjust(11, "0")[-11:],
                          rita_franchigia.rjust(11, "0")[-11:],
                          rita_cto_perc.rjust(11, "0")[-11:],
                          rita_cto_ditt.rjust(11, "0")[-11:],
                          filler.ljust(11, " ")[-11:],
                          rita_data.rjust(8, "0")[-8:],
                          rita_totdoc.rjust(11, "0")[-11:],
                          rita_impvers.rjust(11, "0")[-11:],
                          rita_data_i.rjust(8, "0")[-8:],
                          rita_data_f.rjust(8, "0")[-8:],
                          emens_att.rjust(2, "0")[-2:],
                          emens_rap.rjust(2, "0")[-2:],
                          emens_ass.rjust(3, "0")[-3:],
                          filler.rjust(195, " "),
                          por_codpag.rjust(3, "0")[-3:],
                          por_banca.rjust(5, "0")[-5:],
                          por_agenzia.rjust(5, "0")[-5:],
                          por_desagenzia.ljust(30, " ")[-30:],
                          por_tot_rate.rjust(2, "0")[-2:],
                          por_totdoc.rjust(12, "0")[-12:],
                          tab_det_eff,
                          por_codage.rjust(4, "0")[-4:],
                          por_effetto_sosp.ljust(12, " ")[-12:],
                          filler.ljust(324, " "),
                          tabella_mov_interstat_ben,
                          tab_mov_interstat_servizi,
                          intra_tipo_servizio.ljust(1, " ")[-1:],
                          serv_mese_anno_rif.rjust(6, "0")[-6:],
                          tab_check_iva,
                          xnum_doc_ori.ljust(15, " ")[-15:],
                          filler.rjust(1091, " "),
                          filler.ljust(2, " "),
                          ]

        return record_opzione

    def _selectmovetype(self, target_move, date_from, date_to, cr, uid):

        active_model = ""
        res_out = []

        if target_move == 'Rs':

            active_model = 'account.move'

            query_str = '''SELECT DISTINCT account_move.id
                           FROM account_move
                           LEFT JOIN account_move_line
                           ON account_move.id=account_move_line.move_id
                           WHERE account_move_line.stored_invoice_id IS NULL
                             AND account_move.state NOT IN ( 'draft', 'cancel')
                             AND (account_move.date BETWEEN '''+"'"+str(date_from)+"'"+''' AND '''+"'"+str(date_to)+"'"+''')
                           '''

            cr.execute(query_str)
            res = cr.fetchall()

            if len(res) > 0:
                for line in res:
                    res_out.append(line[0])

        elif target_move == 'Fc':
            active_model = 'account.invoice'
            res_out = self.pool.get('account.invoice').search(cr, uid,
                                                              [('registration_date', '>=', date_from),
                                                               ('registration_date', '<=', date_to),
                                                               ('state', 'not in', ['draft', 'cancel']),
                                                               ('type', '=', 'out_invoice')],
                                                              order="number")

        elif target_move == 'Ncc':
            active_model = 'account.invoice'
            res_out = self.pool.get('account.invoice').search(cr, uid,
                                                              [('registration_date', '>=', date_from),
                                                               ('registration_date', '<=', date_to),
                                                               ('state', 'not in', ['draft', 'cancel']),
                                                               ('type', '=', 'out_refund')],
                                                              order="number")

        elif target_move == 'Ncf':
            active_model = 'account.invoice'
            res_out = self.pool.get('account.invoice').search(cr, uid,
                                                              [('registration_date', '>=', date_from),
                                                               ('registration_date', '<=', date_to),
                                                               ('state', 'not in', ['draft', 'cancel']),
                                                               ('type', '=', 'in_refund')],
                                                              order="number")

        elif target_move == 'Ff':
            active_model = 'account.invoice'
            res_out = self.pool.get('account.invoice').search(cr, uid,
                                                              [('registration_date', '>=', date_from),
                                                               ('registration_date', '<=', date_to),
                                                               ('state', 'not in', ['draft', 'cancel']),
                                                               ('type', '=', 'in_invoice')],
                                                              order="number")

        elif target_move == 'Ac':
            active_model = 'res.partner'
            res_out = self.pool.get('res.partner').search(cr, uid,
                                                          [('create_date', '>=', date_from),
                                                           ('create_date', '<=', date_to),
                                                           ('customer', '=', 't')])

        elif target_move == 'Af':
            active_model = 'res.partner'
            res_out = self.pool.get('res.partner').search(cr, uid,
                                                          [('create_date', '>=', date_from),
                                                           ('create_date', '<=', date_to),
                                                           ('supplier', '=', 't')])

        return [active_model, res_out]

    def _check_date_range_validity(self, target_move, date_to, date_from):

            date_object_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            date_object_from = datetime.strptime(date_from, '%Y-%m-%d').date()

            if not target_move or(date_object_from.toordinal() > date_object_to.toordinal()):
                raise orm.except_orm('Error', _('Errore sui parametri di ingresso'))

    def _get_records(self, cr, uid, obj_data, active_model, context):

        t_result_list = []

        if obj_data and active_model == "account.move" and self._CODE_CUSTOMER_FLAG:
            t_move_dict = {}
            t_first_partner_id = 0
            t_num_partners = 0

            for line in obj_data.line_id:
                t_partner_id = line.partner_id and line.partner_id.id or 0
                if t_partner_id not in t_move_dict:
                    t_move_dict[t_partner_id] = []
                    if t_partner_id:
                        t_num_partners = t_num_partners + 1
                if not t_first_partner_id and t_partner_id:
                    t_first_partner_id = t_partner_id
                t_move_dict[t_partner_id].append(line.id)
            if t_first_partner_id and 0 in t_move_dict:
                t_move_dict[t_first_partner_id] += t_move_dict[0]
                del t_move_dict[0]

            t_counter = 0
            for t_partner_id in t_move_dict:
                t_is_first = True
                if t_counter:
                    t_is_first = False
                t_is_last = False
                if t_counter == t_num_partners - 1:
                    t_is_last = True
                t_counter = t_counter + 1

                context.update({'t_partner_id': t_partner_id,
                                't_is_first': t_is_first,
                                't_is_last': t_is_last,
                                't_line_list': t_move_dict[t_partner_id],
                                })
                record_01 = self._layoutrecord(obj_data, active_model, cr, uid, context=context)
                t_result_list.append((record_01, " "))

            return t_result_list

        record_01 = self._layoutrecord(obj_data, active_model, cr, uid, context=context)

        if active_model == "account.invoice":
            record_02 = self._optionalrecord(obj_data, active_model, cr, uid)
            t_result_list.append((record_01, record_02))

        else:
            t_result_list.append((record_01, " "))

        return t_result_list

    def act_getfile(self, cr, uid, ids, context=None):

        active_model = context and context.get('active_model', [])
        active_ids = context and context.get('active_ids', [])
        array_fatture = []

        # selezione manuale delle voci
        if active_ids and active_model:
            active_model_obj = self.pool.get(active_model)
            obj_data = active_model_obj.browse(cr, uid, active_ids, context=context)

            for data in obj_data:
                if active_model == "res.partner" or (data.state != "draft" and data.state != "cancel"):

                    t_result = self._get_records(cr, uid, obj_data, active_model, context=context)
                    array_fatture = array_fatture + t_result

                else:
                    out = base64.encodestring(self._creaFile(array_fatture).encode("ascii"))
                    self.write(cr, uid, ids, {'state': 'get', 'export_file_txt': out}, context=context)
                    raise orm.except_orm('Error',
                                         _('Fattura non estraibile. Selezionare solo fatture aperte o pagate!'))

            out = base64.encodestring(self._creaFile(array_fatture).encode("ascii"))
            self.write(cr, uid, ids, {'state': 'get', 'export_file_txt': out}, context=context)

        # selzione esporta verso gecom teamsystem tra intervallo di date
        # se le date non sono specificate esporta tutto
        elif not active_model:

            wizard_read = self.read(cr, uid, ids[0], ['target_move', 'date_to', 'date_from'], context=context)

            target_move = wizard_read['target_move']
            date_to = wizard_read['date_to'] or '9999-01-12'
            date_from = wizard_read['date_from'] or '1753-01-01'

            self._check_date_range_validity(target_move, date_to, date_from)

            [active_model, res] = self._selectmovetype(target_move, date_from, date_to, cr, uid)

            if not res:
                raise orm.except_orm('Error', _('Nessun Risultato'))

            active_model_obj = self.pool.get(active_model)
            for obj_data in active_model_obj.browse(cr, uid, res, context=context):

                t_result = self._get_records(cr, uid, obj_data, active_model, context=context)
                array_fatture = array_fatture + t_result

            out = base64.encodestring(self._creaFile(array_fatture).encode("utf8"))
            self.write(cr, uid, ids,
                       {'state': 'get',
                        'export_file_txt': out,
                        'date_from': date_from,
                        'date_to': date_to},
                       context=context)

        else:
            raise orm.except_orm('Error', _('Selezionare almeno una voce'))

        model_data_obj = self.pool.get('ir.model.data')
        view_rec = model_data_obj.get_object_reference(cr, uid,
                                                       'account_export_teamsystem_readytec',
                                                       'wizard_invoice_file_export')
        view_id = view_rec and view_rec[1] or False

        return {'view_type': 'form',
                'view_id': [view_id],
                'view_mode': 'form',
                'res_model': 'invoice.file.export',
                'res_id': ids[0],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': context,
                }

    _name = "invoice.file.export"

    _columns = {
        'state': fields.selection((('choose', 'choose'),   # choose accounts
                                   ('get', 'get'),         # get the file
                                   )),

        'export_file_txt': fields.binary('File', readonly=True),

        'date_from': fields.date('Dalla Data'),

        'date_to': fields.date('Alla Data'),

        'target_move': fields.selection([('Rs', 'Registrazioni Sezionale'),
                                         ('Fc', 'Fatture Clienti '),
                                         ('Ncc', 'Note di Credito Clienti'),
                                         #  ('Ff', 'Fatture Fornitori'),
                                         #  ('Ncf', 'Note di Credito Fornitori'),
                                         ('Ac', 'Anagrafiche clienti'),
                                         ('Af', 'Anagrafiche fornitori'),
                                         ], 'Registrazioni', required=True),
    }

    _defaults = {'state': lambda *a: 'choose',
                 'target_move': 'Rs',
                 }
