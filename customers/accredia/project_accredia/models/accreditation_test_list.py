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

from openerp import fields, models, api


class AccreditationTestList(models.Model):

    _name = "accreditation.test.list"
    _description = "Righe prove accreditate"

    test_id = fields.Many2one('accreditation.test', 'Prova Accreditata')
    ref_excel = fields.Integer('Riferimento di riga (colonna N° modello excel)')
    material_product_matrix = fields.Text('Materiale/Prodotto/Matrice')
    property = fields.Text('Misurando/proprietà misurata/Denominazione della prova')
    measure = fields.Text('Campo di misura e/o di prova')
    technique = fields.Text('Tecnica di prova')
    method = fields.Text('Metodo di prova ed anno di emissione')
    category_id = fields.Many2one('accreditation.test.list.category', 'Categoria')
    state = fields.Selection([('A', 'Accreditato'),
                              ('N', 'Non accreditato'),
                              ('S', 'Sospeso Marchio'),
                              ], 'Stato',
                             select=True)
    state_write_date = fields.Datetime('Data/Ora Ultima Modifica')
    state_write_uid = fields.Many2one('res.users', 'Utente')

    @api.multi
    @api.depends('test_id.rev_number', 'test_id.unit_id.name')
    def name_get(self):
        res = []
        for rp in self:
            t_rev = rp.test_id and rp.test_id.rev_number and str(rp.test_id.rev_number) or ''
            descr = ("%s") % (t_rev)
            descr += (" - %s") % (rp.test_id.rev_number)
            if rp.test_id.unit_id:
                descr += (" - %s") % (rp.test_id.unit_id.name)
            res.append((rp.id, descr))
        return res
