# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012-2013:
#        Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
try:
    import json
except ImportError:
    import simplejson as json

import openerp.http as http
from openerp.http import request
import openerp
import StringIO
import zipfile
from openerp.report import render_report


class ExportZipFIle(openerp.http.Controller):

    @http.route('/web/export/zip_invoices', type='http', auth='user')
    def export_zip_invoices(self, data, token):
        data = json.loads(data)

        in_memory_zip = StringIO.StringIO()
        zf = zipfile.ZipFile(in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        rows = data.get('rows', [])
        rows = [int(x) for x in rows]
        for row in rows:
            account_obj = request.env['account.invoice'].browse(row);
            (result, format) = render_report(request.cr, request.uid,[ account_obj.id], 'fatturadiff', data)
            filename = account_obj.number.replace('/','')
            if not filename:
                filename = 'invoice_' + str(row)
            zf.writestr(filename + '.' + format.encode("utf-8"), result)
        zf.close()
        in_memory_zip.seek(0)
        data = in_memory_zip.read()

        return request.make_response(
            data,
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % 'invoices.zip'),
                ('Content-Type', 'application/zip')
            ],
            cookies={'fileToken': token}
        )