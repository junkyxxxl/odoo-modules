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

from openerp import fields, models


class AccreditationTaskWorkLog(models.Model):

    _name = 'accreditation.task.work.log'

    doclite_action_type = fields.Selection([('create_audit', 'Generazione Attività di Audit'),
                                            ('display_to_plan_audit', 'Mostra Audit da pianificare'),
                                            ('create_line_to_invoice', 'Generazione Riga da Fatturare a Cliente'),
                                            ('create_quotation', 'Generazione Preventivo per Fornitore'),
                                            ('create_purchase_requisition', 'Generazione Richiesta di Acquisto'),
                                            ('create_sale_quotation', 'Generazione Preventivo per Cliente'),
                                            ('create_advance_invoice', 'Generazione Fattura Acconto'),
                                            ('update_agenda', 'Scrittura su Agenda Ispettore'),
                                            ('accreditation_request_generation', 'Generazione Domanda Accreditamento'),
                                            ('set_obtained_accreditation', 'Imposta Accreditamento/Riconoscimento ottenuto'),
                                            ('del_obtained_accreditation', 'Elimina Accreditamento/Riconoscimento ottenuto'),
                                            ('create_maintenance_fee_tasks', 'Crea Attività Diritti di Mantenimento'),
                                            ('create_maintenance_fee_offer', 'Crea Preventivo Diritti di Mantenimento'),
                                            ('create_child_project', 'Creazione Pratica Collegata'),
                                            ('get_accreditation_test', 'Richiamo Elenco Prove Accreditate'),
                                            ('doclite_action', 'Azione DocLite '),
                                            ],
                                           'Tipo Azione', select=True)
    state = fields.Selection([('ok', 'OK'),
                              ],
                             'Esito', select=True)
    work_id = fields.Many2one('project.task.work', 'Azione')

    # risultati
    action_url = fields.Char('Link DocLite', default='')
    to_plan_project_id = fields.Many2one('project.project', 'Audit da pianificare')
    phase_id = fields.Many2one('project.phase', 'Audit')
    analytic_line_id = fields.Many2one('account.analytic.line', 'Attività da Fatturare')
    purchase_order_id = fields.Many2one('purchase.order', 'Preventivo Fornitore')
    purchase_requisition_id = fields.Many2one('purchase.requisition', 'Richiesta di Acquisto')
    sale_order_id = fields.Many2one('sale.order', 'Preventivo Cliente')
    advance_invoice_id = fields.Many2one('account.invoice', 'Fattura Acconto')
    meeting_id = fields.Many2one('calendar.event', 'Meeting')
    request_id = fields.Many2one('accreditation.request', 'Domanda Accreditamento')
    child_project_id = fields.Many2one('project.project', 'Pratica Collegata')
    project_task_id = fields.Many2one('project.task', 'Attività Diritti di Mantenimento')
    exec_date = fields.Datetime('Data e Ora')
    user_id = fields.Many2one('res.users', 'Utente')
    doclite_action_name = fields.Char('Azione')
