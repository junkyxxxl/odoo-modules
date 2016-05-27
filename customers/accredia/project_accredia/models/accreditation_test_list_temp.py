# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models


class AccreditationTestListTemp(models.Model):

    _name = "accreditation.test.list.temp"
    _description = "Righe prove accreditate (Tabella temporanea)"

    test_id = fields.Many2one('accreditation.test.temp', 'Prova Accreditata (temporanea)')
    ref_excel = fields.Integer('Riferimento di riga (colonna N° modello excel)')

    measure = fields.Text('Campo di misura e/o di prova')
    measure_old = fields.Text()

    material_product_matrix = fields.Text('Materiale/Prodotto/Matrice')
    material_product_matrix_old = fields.Text()

    property = fields.Text('Misurando/proprietà misurata/Denominazione della prova')
    property_old = fields.Text()

    method = fields.Text('Metodo di prova ed anno di emissione')
    method_old = fields.Text()

    technique = fields.Text('Tecnica di prova')
    technique_old = fields.Text()

    category_id = fields.Many2one('accreditation.test.list.category', 'Categoria')
    add_row = fields.Boolean('Riga aggiunta')

    var_material_product_matrix = fields.Boolean('Variato Materiale/Prodotto/Matrice')
    var_property = fields.Boolean('Variato Misurando/proprietà misurata/Denominazione della prova')
    var_measure = fields.Boolean('Variato Campo di misura e/o di prova (Campo boolean)')
    var_technique = fields.Boolean('Variato Tecnica di prova (Campo boolean)')
    var_method = fields.Boolean('Variato Metodo di prova ed anno di emissione')
    var_category = fields.Boolean('Variato Categoria')

    test_list_id = fields.Many2one('accreditation.test.list', 'Riferimento elenco prove (se proveniente da elenco prove accreditate)')

    var_type_id = fields.Many2one('accreditation.test.change.type', 'Variazione richiesta')
