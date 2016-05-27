# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 ISA s.r.l. (<http://www.isa.it>).
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
from openerp.exceptions import except_orm


class AccreditationTaskWorkType(models.Model):
    _description = 'Type of work'
    _name = 'accreditation.task.work.type'
    _order = 'code'

    name = fields.Char('Description', size=80, required=True, select=True)
    code = fields.Char('Code', size=3, required=True)
    doclite_action_name = fields.Char('Nome Azione', size=200)
    create_audit = fields.Boolean('Generazione Attività di Audit')
    create_line_to_invoice = fields.Boolean('Generazione Riga da Fatturare a Cliente')
    create_quotation = fields.Boolean('Generazione Preventivo per Fornitore',
                                      help = "Se la persona fisica è un fornitore, se è impostato il Prodotto Nota Spese,"
                                             "viene creata nel preventivo, un'ulteriore riga con con quantità e valore a zero "
                                             "per la registrazione del rimborso spese dell'ispettore esterno")
    update_agenda = fields.Boolean('Scrittura su Agenda Ispettore')

    type_audit_visit = fields.Many2one('accreditation.task.work.type', 'Tipo Attività Visita')
    type_audit_doc_review = fields.Many2one('accreditation.task.work.type',
                                            'Tipo Attività Esame Documentale')

    accreditation_request_generation = fields.Boolean('Generazione Domanda Accreditamento')

    audit_visit_doc_review = fields.Boolean('Attività di Visita/Esame documentale')
    audit_visit_accompaniment = fields.Boolean('Attività di Visita in Accompagnamento')

    create_purchase_requisition = fields.Boolean('Richiesta ordine di acquisto')
    create_sale_quotation = fields.Boolean('Preventivi clienti')

    product_line_id = fields.Many2one('product.product', 'Prestazione da Fatturare')
    journal_id = fields.Many2one('account.analytic.journal', 'Giornale Analitico')
    to_invoice = fields.Many2one('hr_timesheet_invoice.factor', 'Fatturabile (Creazione attività)')
    to_invoice_close = fields.Many2one('hr_timesheet_invoice.factor', 'Fatturabile (Fine attività)')

    product_quotation_id = fields.Many2one('product.product',
                                           'Prestazione per Preventivo Fornitore')
    product_maintenance_fee_id = fields.Many2one('product.product',
                                                 'Prestazione per Diritti Mantenimento')
    work_type_maintenance_fee_id = fields.Many2one('accreditation.task.work.type',
                                                   domain=[('create_maintenance_fee_offer', '=', True)],
                                                   string='Tipo attività Diritti di Mantenimento')
    accreditation_request_type = fields.Many2one('accreditation.project.type', 'Tipo Domanda')
    accreditation_request_state = fields.Selection([('G', 'Ricevuta'),
                                                    ('E', 'In esame'),
                                                    ('A', 'Accettata'),
                                                    ('R', 'Rifiutata'),
                                                    ],
                                                   "Stato Domanda")

    doclite_action = fields.Boolean('Azione DocLite')

    set_obtained_accreditation = fields.Boolean('Imposta Accreditamento/Riconoscimento ottenuto')
    del_obtained_accreditation = fields.Boolean('Elimina Accreditamento/Riconoscimento ottenuto')

    create_maintenance_fee_tasks = fields.Boolean('Crea Attività Diritti di Mantenimento')
    create_maintenance_fee_offer = fields.Boolean('Crea Preventivo Diritti di Mantenimento')

    create_child_project = fields.Boolean('Crea Pratica Collegata')

    child_project_department_id = fields.Many2one('hr.department', 'Dipartimento')
    child_project_template_id = fields.Many2one('project.project', 'Template Pratica')
    child_project_type_id = fields.Many2one('accreditation.project.type', 'Tipo Pratica')

    get_accreditation_test = fields.Boolean('Richiamo Elenco Prove Accreditate')

    req_supervision = fields.Boolean('Richiesta giorni sorveglianza')

    days_dipendent_authorization = fields.Boolean('Giorni autorizzazione dipendente PA')
    expense_report_supplier = fields.Many2one('product.product',
                                              'Prodotto Nota Spese Per Preventivo Fornitore')

    audit_task_type = fields.Selection(
        [('foreseen', 'Previste'),
         ('to_plan', 'Da Pianificare'),
         ('planned', 'Pianificate')],
        string='Tipo Attività',
        default='planned')

    @api.onchange('set_obtained_accreditation')
    def onchange_set_obtained_accreditation(self):
        if self.set_obtained_accreditation:
            self.del_obtained_accreditation = False

    @api.onchange('del_obtained_accreditation')
    def onchange_del_obtained_accreditation(self):
        if self.del_obtained_accreditation:
            self.set_obtained_accreditation = False

    @api.model
    def create(self, vals):
        # ad eccezione del campo "FATTURABILE" può essere scelto un solo ruolo.
        t_count = 0

        if 'set_obtained_accreditation' in vals and vals['set_obtained_accreditation']:
            t_count = t_count + 1

        if 'del_obtained_accreditation' in vals and vals['del_obtained_accreditation']:
            t_count = t_count + 1

        if t_count > 1:
            raise except_orm(_('Errore'),
                             _("Non è possibile impostare Accreditamento/Riconoscimento ottenuto!"))

        return super(AccreditationTaskWorkType, self).create(vals)

    @api.multi
    def write(self, vals):
        for data in self:

            t_count = 0

            if 'set_obtained_accreditation' in vals and vals['set_obtained_accreditation']:
                t_count = t_count + 1
            elif 'set_obtained_accreditation' not in vals:
                if data.set_obtained_accreditation:
                    t_count = t_count + 1

            if 'del_obtained_accreditation' in vals and vals['del_obtained_accreditation']:
                t_count = t_count + 1
            elif 'del_obtained_accreditation' not in vals:
                if data.del_obtained_accreditation:
                    t_count = t_count + 1

            if t_count > 1:
                raise except_orm(_('Errore'),
                                 _("Non è possibile impostare più di un ruolo!"))

        return super(AccreditationTaskWorkType, self).write(vals)
