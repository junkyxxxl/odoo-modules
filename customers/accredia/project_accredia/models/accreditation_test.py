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

from openerp.osv import fields, orm
from openpyxl import *
from io import BytesIO
import StringIO
import base64
import xlwt
import xlrd
from xlutils.copy import copy
import os


class accreditation_test(orm.Model):

    _name = "accreditation.test"
    _description = "Testata prove accreditate"

    _order = 'rev_number desc'

    def _is_last_rev(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for d in self.browse(cr, uid, ids, context=context):
            res[d.id] = False
            t_max_test_data = None
            if d.project_id:
                for test_data in d.project_id.test_ids:
                    if not t_max_test_data or (test_data.rev_number and t_max_test_data.rev_number and t_max_test_data.rev_number < test_data.rev_number):
                        t_max_test_data = test_data

                if t_max_test_data and t_max_test_data.rev_number == d.rev_number:
                    res[d.id] = True
        return res

    _columns = {'test_list_ids': fields.one2many('accreditation.test.list',
                                                 'test_id',
                                                 'Righe Prove Accreditate'),
                'rev_date': fields.date('Data Revisione'),
                'rev_number': fields.integer('Numero Revisione', required=True),
                'unit_id': fields.many2one('accreditation.units', 'Unità di riferimento'),
                'project_id': fields.many2one('project.project', 'Pratica', required=True),
                'active': fields.boolean('Attivo'),
                'state': fields.selection([('draft', 'Bozza'),
                                           ('open', 'In Elaborazione'),
                                           ('error', 'Errore'),
                                           ('done', 'Completato')],
                                          'Stato'),
                'filedata': fields.binary('File', filters='*.xlsx,*.xls'),
                'filename': fields.char('Filename'),                
                'test_temp_id': fields.many2one('accreditation.test.temp', 'Rif. Prova Temporanea'),
                'is_last_rev': fields.function(_is_last_rev,
                                               string='Ultima Revisione',
                                               type='boolean'),
                'partner_id': fields.related('unit_id',
                             'partner_id',
                             type='many2one',
                             relation='res.partner',
                             string='Partner'),
                }

    _defaults = {'active': True,
                 'state': 'draft',
                 'rev_number': 0,
                 }

    def create_model_da02(self, cr, uid, ids, default={}, context=None):
        t_template = os.path.dirname(os.path.realpath(__file__)) + '/../template/FileDestinazione.xls'
        accreditation_test_obj= self.browse(cr,uid,ids[0],context)
        rb = xlrd.open_workbook(t_template, formatting_info=True)
        wb = copy(rb)
        ws = wb.get_sheet(2)
        acc_list = self.pool.get('accreditation.test.list')
        t_line_ids = acc_list.search(cr, uid, [('test_id', '=', ids[0] )], context=None)
        i = 23
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        style.borders.bottom = 1
        style.borders.left = 1
        style.borders.right = 1
        style.borders.top = 1

        for acc_test_line in acc_list.browse(cr, uid, t_line_ids, context): 
            ws.write(i, 0, i-22                                     ,style)
            ws.write(i, 1, acc_test_line.ref_excel                  ,style)   
            ws.write(i, 2, acc_test_line.material_product_matrix    ,style)
            ws.write(i, 3, acc_test_line.property                   ,style)
            ws.write(i, 4, acc_test_line.measure                    ,style)
            ws.write(i, 5, acc_test_line.technique                  ,style)
            ws.write(i, 6, acc_test_line.method                     ,style)
            ws.write(i, 7, acc_test_line.category_id.code           ,style)
            ws.write(i, 8, None                                     ,style)
            ws.write(i, 9, None                                     ,style)
            i += 1

        output = StringIO.StringIO()
        wb.save(output)
        out = base64.encodestring(output.getvalue())
        project_id = accreditation_test_obj.project_id.id
        filename = self.pool.get('accreditation.test.temp').getFileName(cr, uid,project_id,context) + 'v' + str(accreditation_test_obj.rev_number) + '.xls'
        self.write(cr, uid, ids[0], {'filedata': out, 'filename': filename.replace(' ', ''), 'state': 'done'})
        return True

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        res = []
        for rp in self.browse(cr, uid, ids):
            descr = ("%d") % (rp.rev_number)
            if rp.unit_id:
                descr = ("%s - %d") % (rp.unit_id.name, rp.rev_number)
            elif rp.project_id:
                descr = ("%s - %d") % (rp.project_id.name, rp.rev_number)
            res.append((rp.id, descr))
        return res
