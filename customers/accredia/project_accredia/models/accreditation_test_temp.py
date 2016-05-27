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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import api
from openerp.tools.translate import _
from io import BytesIO
import xlrd
import StringIO
from xlutils.copy import copy


class accreditation_test_temp(models.Model):

    _name = "accreditation.test.temp"
    _description = "Testata prove accreditate (Tabella temporanea)"
    
    test_list_ids = fields.One2many('accreditation.test.list.temp',
                                                 'test_id',
                                                 'Righe Prove Accreditate')
    
    project_id = fields.Many2one('project.project', 'Pratica', required=True)
    unit_id = fields.Many2one('accreditation.units', 'Unità di riferimento')
    note = fields.Text('Note')
    legenda = fields.Text('Legenda')
    state = fields.Selection([('draft', 'Bozza'),
                              ('open', 'In Elaborazione'),
                              ('error', 'Errore'),
                              ('done', 'Completato')],
                              'Stato',
                            required=True)
    filedata = fields.Binary('File', filters='*.xlsx,*.xls')
    filename = fields.Char('Filename')
    test_final_ids = fields.One2many('accreditation.test','test_temp_id','Prove accreditate')
    partner_id = fields.Many2one(related='project_id.partner_id',
                                 string='Partner',
                                 store=False)

    _defaults = {'state': 'draft',
                 }

    def do_refresh(self):
        return True
    
    @api.multi
    def set_draft(self):
        if self.state == 'error' or self.state == 'done':
            self.write({'state': 'draft',
                        'filedata' : None,
                        'filename' : None,
                                      })
        for t_data_line in self.test_list_ids:
            t_data_line.unlink()
        return True
    
    @api.multi
    def do_process(self):
        if (not self.filedata):
            raise Warning('Attenzione: non è stato caricato nessun file')
        filedata = self.filedata.decode('base64')

        rb = xlrd.open_workbook(file_contents=filedata)
        ws = rb.sheet_by_name('Sez.2 Prove')

        i = 22
        add_row = False
        empty_test = True
        if self.test_list_ids:
            empty_test = False
        
        t_accreditation_test = self.env["accreditation.test"].search([('test_temp_id','=',self.id)],order = 'rev_number desc')
        
        if (not t_accreditation_test):
            while i < (ws.nrows -1):
                test_list_dict = []
                test_list_dict.append(('test_id', self.id))
                i += 1
                test_list_dict.append(('material_product_matrix', ws.cell(i,2).value))
                test_list_dict.append(('property', ws.cell(i,3).value))
                test_list_dict.append(('measure', ws.cell(i,4).value))
                test_list_dict.append(('technique', ws.cell(i,5).value))
                test_list_dict.append(('method', ws.cell(i,6).value))
                category_obj = self.env['accreditation.test.list.category']
                t_categories = category_obj.search([('code', '=', str(ws.cell(i,7).value))])
                if (not t_categories):
                    raise except_orm(_('Nessuna categoria trovata!'),
                                     _("Attenzione categoria prova non presente in anagrafica '%s'!") % (ws.cell(i,7).value,))
                test_list_dict.append(('category_id', t_categories[0].id)) 
                test_list_dict.append(('add_row', add_row)) 
                test_tmp_line = self.env['accreditation.test.list.temp'].create(test_list_dict)
                if ws.cell(i,1).value == '':
                    test_tmp_line.write({'ref_excel': test_tmp_line.id})
                else:
                    test_list_dict.append(('ref_excel', int(ws.cell(i,1).value)))
        else:
            while i < (ws.nrows -1):
                test_list_dict = []
                test_list_dict.append(('test_id', self.id))
                i += 1
                t_line = t_accreditation_test[0].test_list_ids.filtered(lambda r:r.ref_excel == int(ws.cell(i,1).value))
                test_list_dict.append(('ref_excel', int(ws.cell(i,1).value)))
                test_list_dict.append(('material_product_matrix', ws.cell(i,2).value))

                test_list_dict.append(('material_product_matrix_old', t_line.material_product_matrix))
                if t_line.material_product_matrix != ws.cell(i,2).value:
                    test_list_dict.append(('var_material_product_matrix', True))
                test_list_dict.append(('property', ws.cell(i,3).value))

                test_list_dict.append(('property_old',  t_line.property))
                if t_line.property != ws.cell(i,3).value:
                    test_list_dict.append(('var_property', True))
                test_list_dict.append(('measure', ws.cell(i,4).value))                    

                test_list_dict.append(('measure_old', t_line.measure))
                if t_line.measure != ws.cell(i,4).value:
                    test_list_dict.append(('var_measure', True))
                test_list_dict.append(('technique', ws.cell(i,5).value)) 

                test_list_dict.append(('technique_old', t_line.technique))
                if t_line.technique != ws.cell(i,5).value:
                    test_list_dict.append(('var_technique', True))
                test_list_dict.append(('method', ws.cell(i,6).value)) 

                test_list_dict.append(('method_old', t_line.method))
                if t_line.method != ws.cell(i,6).value:
                    test_list_dict.append(('var_method', True))          
                if (ws.cell(i,7)):
                    t_categories = self.env['accreditation.test.list.category'].search([('code', '=', str(ws.cell(i,7).value))])
                    if (not t_categories):
                        raise except_orm(_('Nessuna categoria trovata!'),
                                         _("Attenzione categoria prova non presente in anagrafica '%s'!") % (str(ws.cell(i,7).value),))
                    else:
                        test_list_dict.append(('category_id', t_categories[0].id))
                        if (t_line.category_id.id != t_categories[0].id):  
                            test_list_dict.append(('var_category', True))                  
                if (ws.cell(i,8).value):
                    var_type_id = self.env['accreditation.test.change.type'].search([('code', '=', ws.cell(i,8).value)])[0].id  
                    if (not var_type_id):
                        raise except_orm(_('Nessun tipo variazione trovato!'),
                                     _("Attenzione tipo variazione non presente in anagrafica '%s'!") % (ws.cell(i,8).value,))
                    test_list_dict.append(('var_type_id', var_type_id))
                self.env['accreditation.test.list.temp'].create(test_list_dict) 
        self.state = 'done'  
        return True

    @api.multi
    def wizard_final_test(self):
        context =   {'default_test_temp_id' : self.id,
                     'default_project_id' : self.project_id.id,
                     'default_unit_id' : self.unit_id.id}
        return {
                "type": "ir.actions.act_window",
                "res_model": "wizard.final.test",
                "views": [[False, "form"]],
                "target": "new",
                "context": context

            }

    @api.multi
    def name_get(self):
        res = []
        t_note = self.note or 'Prova Accreditata'
        descr = ("%s") % (t_note)
        if self.unit_id:
            descr = ("%s - %s") % (t_note, self.unit_id.name)
        res.append((self.id, descr))
        return res

    @api.onchange('project_id')
    def onchange_project(self):
        self.unit_id = None
    
    @api.multi    
    def write(self, values):
        if (values.get('filename')):
            filename = self.getFileName(self.project_id.id)
            values.update({'filename' : (filename + '.xls').replace(' ', '') })
        return super(accreditation_test_temp,self).write(values)

    @api.model    
    def create(self, values):
        if (values.get('filename')):
            filename = self.getFileName(values.get('project_id'))
            values.update({'filename' : (filename + '.xls').replace(' ', '') })
        return super(accreditation_test_temp,self).create(values)    

    @api.model
    def getFileName(self, project_id):
        prj_obj = self.env["project.project"].browse(project_id).name
        name1 = prj_obj[0:prj_obj.find('-')]
        rest =  prj_obj[prj_obj.find('-')+1:]
        name = "DA02-All - " + name1 + rest[0:rest.find('-')]
        return name
    
