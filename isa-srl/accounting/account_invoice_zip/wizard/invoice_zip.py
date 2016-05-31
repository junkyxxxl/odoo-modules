# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
import StringIO
import zipfile
from openerp.report import render_report
import base64
try:
    import json
except ImportError:
    import simplejson as json

#Rispetto ai modelli normali, quando si crea un Wizard, bisogna specificare invece che (model.Models) -> (models.TransientModel)

class wizard_invoice_zip(models.TransientModel):
    _name="wizard.invoice"
    filedata = fields.Binary('File', filters='*.zip')
    filename = fields.Char('filename')

    @api.model
    def _get_default_report(self):
      report_id= self.env.user.company_id.invoice_report
      return report_id

    invoice_report = fields.Many2one('ir.actions.report.xml', string="Report fatture", required = True, default=_get_default_report)
    @api.multi
    def create_invoice_zip(self):
        invoice_ids = self.env.context.get('active_ids')
        in_memory_zip = StringIO.StringIO()
        zf = zipfile.ZipFile(in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
        data = {"model":"account.invoice","rows":["1557","1558","1559"]}
        lista = ""
        for record in invoice_ids:
            account_obj = self.env['account.invoice'].browse(record);
            (result, format) = render_report(self._cr, self._uid, [account_obj.id], self.invoice_report.report_name,data)
            filename = account_obj.number.replace('/', '')
            lista += filename +"\n"
            if not filename:
                filename = 'invoice_' + str(record)
            zf.writestr(filename + '.' + format.encode("utf-8"), result)
        zf.close()
        in_memory_zip.seek(0)
        data = in_memory_zip.read()
        self.filedata = base64.encodestring(data)
        print lista
        self.filename = filename


        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(self._cr, self._uid, 'account_invoice_zip', 'zip_invoice_form_view')
        view_id = result and result[1] or False

        obj_id = self.env['invoice.zip'].create({'filename':'Invoice_Zip.zip','filedata':self.filedata,'type':self.invoice_report.name,'element':lista})

        return {
            'name': ('Invoice Zip'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'invoice.zip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': view_id,
            'views': [(view_id, 'form'), (False, 'tree')],
            'res_id':obj_id.id
        }
