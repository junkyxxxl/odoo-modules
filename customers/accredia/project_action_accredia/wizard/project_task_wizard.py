# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.exceptions import except_orm
from dateutil.relativedelta import relativedelta

#Rispetto ai modelli normali, quando si crea un Wizard, bisogna specificare invece che (model.Models) -> (models.TransientModel)
#e quando ho a che fare con l'email, bisogna ereditare "mail.thread" che si occupa della gestione di invio delle email.
class project_task_wizard(models.TransientModel):

    _name="project.task.wizard"

    date_obtained_accreditation = fields.Date(string="Data di accreditamento", required=True, default= fields.Date.today())
    date_delete_accreditation = fields.Date(string="Data di fine accreditamento", required=True, default=fields.Date.today())


    @api.multi
    def send_button(self):
        project_task_work_id = self.env.context.get('project_task_work_id')
        project_task_work_obj = self.env['project.task.work'].browse(project_task_work_id)

        project_task_obj = project_task_work_obj.task_id
        project_project_obj = project_task_obj.project_id

        #Controllo se nel tipo Azione, è stato settato a True, il campo "richiesta giorni sorveglianza"
        type_id_req_supervision = project_task_work_obj.type_id.req_supervision
        task_id_obj = project_task_work_obj.task_id
        if type_id_req_supervision:
            #Se è a true, allora effettuo il controllo sui giorni di sorveglianza dell'attività
            if task_id_obj.req_supervision_days == 0:
                raise except_orm(_('Errore!'),
                            ('Il campo Giorni per Sorveglianza non deve essere uguale a zero nell\'attività!'))

        #Il settaggio della data di accreditamento, lo eseguo solo per chi ha come "Tipo di azione",
        #il campo "set_obtained_accreditation" settato a true

        #Ora setto nel project_task_work la data di accreditamento, che è stata impostata nel wizard
        if (project_task_work_obj.type_id.set_obtained_accreditation):
            #Ora setto nella pratica, la data di accreditamento e modifico la data di scadenza accreditamento nella pratica
            project_project_obj.accreditation_date = self.date_obtained_accreditation

        #Converto la data:
        accreditation_date_format = datetime.strptime(project_project_obj.accreditation_date, DF)
        project_project_obj.accreditation_due_date = accreditation_date_format + timedelta(days=(365*4)-1)

        #Ora modifico nella pratica, la data scadenza invio domanda di accreditamento:
        accreditation_due_data_format = datetime.strptime(project_project_obj.accreditation_due_date, DF)
        project_project_obj.accreditation_request_due_date = accreditation_due_data_format - relativedelta(months=4)

        if (project_task_work_obj.type_id.del_obtained_accreditation):
            #Ora setto nella pratica, la data di fine accreditamento
            project_project_obj.accreditation_expiry_date = self.date_delete_accreditation

        project_task_work_obj.do_action()



