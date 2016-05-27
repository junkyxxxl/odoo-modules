# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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

from openerp import models, fields, api


class wizard_final_test(models.TransientModel):
    _name = 'wizard.final.test'

    dateCert = fields.Date('Data di revisione', default = fields.Date.today())
    test_temp_id = fields.Many2one('accreditation.test.temp', 'Elenco Prove')
    project_id = fields.Many2one('project.project', 'Pratica')
    unit_id = fields.Many2one('accreditation.units', 'Unità di riferimento')

    @api.multi
    def create_final_test(self):
        t_test = []
        t_rev_number = 0
        test_ids = self.env["accreditation.test"].search(
                                                    [('test_temp_id', '=', self._context['active_id'])],
                                                    order="rev_number desc")
        if test_ids:
            t_rev_number = test_ids[0].rev_number + 1
            
        test_dict = {'active': True,
                     'state': 'draft',
                     'test_list_ids': [],
                     'rev_date': self.dateCert,
                     'rev_number': t_rev_number,
                     'test_temp_id': self._context['active_id'],
                     'file': None,
                     'project_id': self._context['default_project_id'],
                     'unit_id': self._context['default_unit_id']
                     }

        res = self.env["accreditation.test"].create(test_dict)
        t_test.append(res.id)
        #self.env["accreditation.test.temp"].write({'test_final_id': res,})
        
        sort_list = []
        t_temp_id = self._context['active_id']
        test_temp_obj = self.env["accreditation.test.temp"].browse(t_temp_id)
        
        for t_list_data in test_temp_obj.test_list_ids:
            if (t_list_data.var_type_id.code != 'R'):
                t_category = t_list_data.category_id and t_list_data.category_id.name or ''
                t_material = t_list_data.material_product_matrix or ''
                t_property = t_list_data.property or ''
                t_method = t_list_data.method or ''
    
                sort_list += [(t_category, t_material, t_property, t_method, t_list_data.id)]
            
            if (test_ids):
                test_list_item = test_ids[0].test_list_ids.filtered(lambda r:r.ref_excel == t_list_data.ref_excel)
            if (t_list_data.var_type_id.code == 'A' or t_list_data.var_type_id.code == 'N' or t_list_data.var_type_id.code == 'E' or t_list_data.var_type_id.code == 'R'):
                test_list_item.write({'state': 'N'})


        def getKey(item):
            return item[0] + item[1] + item[2] + item[3]

        for t_item in sorted(sort_list, key=getKey):
            test_list_obj = self.env["accreditation.test.list.temp"]
            t_list_data = test_list_obj.browse(t_item[4])

            test_list_dict = {'test_id': res.id,
                              'ref_excel': t_list_data.ref_excel,
                              'measure': t_list_data.measure,
                              'material_product_matrix': t_list_data.material_product_matrix,
                              'property': t_list_data.property,
                              'method': t_list_data.method,
                              'technique': t_list_data.technique,
                              'category_id': t_list_data.category_id and t_list_data.category_id.id or None,
                              'state': 'A',
                              }
                
            self.env["accreditation.test.list"].create(test_list_dict)
        
        for t_list_data in test_temp_obj.browse(t_temp_id).test_list_ids:
            t_list_data.unlink()
        
        test_temp_obj.state = 'draft'
        test_temp_obj.filedata = None
        test_temp_obj.filename = None    
        
        if res:
            return {
                "type": "ir.actions.act_window",
                "res_model": "accreditation.test",
                "views": [[False, "tree"],[False, "form"]],
                'domain': [('test_temp_id','=', self._context['active_id'])],
                }
        return True
