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

import glob
import logging
import os
import re
from openerp.tools.translate import _
from openerp.osv import orm, fields
from openerp.exceptions import except_orm


class wizard_document_importer(orm.TransientModel):

    _name = "wizard.document.importer"

    _columns = {'url': fields.char('Url', size=1024),
                'root_id': fields.many2one('document.directory','Root')
        }

    def _iterate_file_system(self, cr, uid, ids, base_path, path, root_id, context = None):
        if len(path)>0 and path[-1] != '/':
            path = path+'/'
        if os.path.exists(base_path+path): 
            r = os.listdir(base_path+path)
            for entry in r:
                if os.path.isdir(base_path+path+entry):
                    print 'folder: '+base_path+path+entry
                    self._create_folder(cr, uid, ids, path+entry, root_id, context)
                    self._iterate_file_system(cr,uid,ids,base_path,path+entry, root_id, context)
            for entry in r:                
                if os.path.isfile(base_path+path+entry):
                    print 'file: '+base_path+path+entry
                    self._create_document(cr, uid, ids, base_path, path+entry, root_id, context)
                #for f in entry:
                #    print root+f+'\n'
                #for d in dirs:
                #    self._iterate_file_system(cr, uid, ids, root+d, context)

    def _create_folder(self, cr, uid, ids, path, root_id, context=None):
        folder_obj = self.pool.get('document.directory')
        vals = {}
        my_id = root_id
        if path != '':
            tree = path.split('/')
            name = tree[-1]
            del tree[-1]
            for i in range(0,len(tree)):
                folder_data = folder_obj.search(cr,uid,[('name','ilike',tree[i]),('parent_id','=',my_id)])
                my_id = folder_data[0]
            vals.update({'name': name})
            vals.update({'type': 'directory'})
            vals.update({'parent_id':my_id})
        return folder_obj.create(cr,uid,vals,context)

    def _create_document(self, cr, uid, ids, base_path, path, root_id, context=None):
        attach_obj = self.pool.get('ir.attachment')
        folder_obj = self.pool.get('document.directory')        
        vals = {}
        my_id = root_id
        if path != '':
            tree = path.split('/')
            name = tree[-1]
            del tree[-1]
            for i in range(0,len(tree)):
                folder_data = folder_obj.search(cr,uid,[('name','ilike',tree[i]),('parent_id','=',my_id)])
                my_id = folder_data[0]
            vals.update({'name': name})
            vals.update({'type': 'url'})
            vals.update({'parent_id':my_id})
            vals.update({'url': base_path+path})
        return attach_obj.create(cr,uid,vals,context)

    def import_attachments(self, cr, uid, ids, context=None):

        if(not ids[0]):
            raise except_orm(_('Error!'), _('Operation Failed !'))
        wiz_obj = self.browse(cr,uid,ids[0])
        if (not wiz_obj or not wiz_obj.url or not wiz_obj.root_id):
            raise except_orm(_('Error!'), _('Operation Failed !'))

        path = wiz_obj.url
        root_id = wiz_obj.root_id.id
        if path[-1] != '/':
            path = path+'/'
        if os.path.exists(path):
            self._iterate_file_system(cr, uid, ids, path, '', root_id, context)
        else:
            raise except_orm(_('Error!'), _('Operation Failed !'))
        return
