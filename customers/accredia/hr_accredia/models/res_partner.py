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

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.modules import registry


class res_partner_accredia(orm.Model):

    # Entity
    _inherit = "res.partner"

    def create_unit(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for entity_data in self.browse(cr, uid, ids):
            t_street1 = entity_data.street or ''
            t_street2 = entity_data.street2 or ''
            vals = {'partner_id': entity_data.id,
                    'name': entity_data.name or '',
                    'address': t_street1 + ' ' + t_street2,
                    'zip': entity_data.zip or '',
                    'city': entity_data.city or '',
                    'province': entity_data.province and entity_data.province.id or None,
                    'region': entity_data.region and entity_data.region.id or None,
                    'country_id': entity_data.country_id and entity_data.country_id.id or None,
                    'phone': entity_data.phone or '',
                    'phone2': entity_data.mobile or '',
                    'email': entity_data.email or '',
                    'fax': entity_data.fax or '',
                    'active': True,
                    }
            location_obj = self.pool.get('accreditation.locations')
            unit_obj = self.pool.get('accreditation.units')
            new_location_id = location_obj.create(cr, uid, vals, context)

            vals = {'partner_id': entity_data.id,
                    'phone': entity_data.phone or '',
                    'phone2': entity_data.mobile or '',
                    'email': entity_data.email or '',
                    'fax': entity_data.fax or '',
                    'unit_name': entity_data.name or '',
                    'operating_unit': True,
                    'location_id': new_location_id,
                    'active': True,
                    }
            unit_obj.create(cr, uid, vals, context)
        return True

    def change_sensible_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        entity_data = self.browse(cr, uid, ids[0])

        context.update({'default_entity_id': entity_data.id,
                        'default_legal_name': entity_data.name,
                        'default_vat_code': entity_data.vat,
                        'default_fiscal_code': entity_data.fiscalcode,
                        'default_accounting_receivable_code': self._get_receivable_default_code(cr, uid, ids, entity_data.id),
                        'default_accounting_payable_code': self._get_payable_default_code(cr, uid, ids, entity_data.id),
                        'default_street': entity_data.street,
                        'default_city': entity_data.city,
                        'default_zip': entity_data.zip,
                        'default_province': entity_data.province and entity_data.province.id or None,
                        'default_region': entity_data.region and entity_data.region.id or None,
                        'default_country_id': entity_data.country_id and entity_data.country_id.id or None,
                        })

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'hr_accredia',
                                              'view_hr_accredia_changes_entity_form')
        view_id = result and result[1] or False
        return {'name': _('Changes'),
                'res_model': 'hr.accredia.changes.entity',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'view_type': 'form',
                'view_mode': 'form',
                'context': context,
                'target': 'new',
                }

    def _get_replaced_by(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        changelog_obj = self.pool.get('accreditation.changelog')
        for rec in self.browse(cr, uid, ids):
            changelog_ids = changelog_obj.search(cr, uid,
                                                 [('partner_id_old', '=', rec.id)])
            res[rec.id] = None
            if changelog_ids:
                changelog_data = changelog_obj.browse(cr, uid,
                                                      changelog_ids[0])
                res[rec.id] = changelog_data.partner_id_new.id

        return res

    def _get_validity_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        changelog_obj = self.pool.get('accreditation.changelog')
        for rec in self.browse(cr, uid, ids):
            changelog_ids = changelog_obj.search(cr, uid,
                                                 [('partner_id_new', '=', rec.id)])
            res[rec.id] = None
            if changelog_ids:
                changelog_data = changelog_obj.browse(cr, uid,
                                                      changelog_ids[0])
                res[rec.id] = changelog_data.validity_date

        return res

    def _get_replaces(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        changelog_obj = self.pool.get('accreditation.changelog')
        for rec in self.browse(cr, uid, ids):
            changelog_ids = changelog_obj.search(cr, uid,
                                                 [('partner_id_new', '=', rec.id)])
            res[rec.id] = None
            if changelog_ids:
                changelog_data = changelog_obj.browse(cr, uid,
                                                      changelog_ids[0])
                res[rec.id] = changelog_data.partner_id_old.id

        return res

    def _get_property_account_receivable_code(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids):
            res[rec.id] = ''
            if rec.property_account_receivable and rec.property_account_receivable.code:
                res[rec.id] = rec.property_account_receivable.code

        return res

    def _check_user_admin(self, cr, uid, ids, field_name, arg, context=None):

        user_obj = self.pool.get('res.users')
        t_user = user_obj.browse(cr, uid, uid)
        t_user_group_ids = t_user.groups_id
        t_user_flag = False

        for t_group in t_user_group_ids:
            if (not t_user_flag
             and t_group.name == 'Manager'
             and t_group.category_id
             and t_group.category_id.name == 'Human Resources'):
                t_user_flag = True
        res = {}
        for rec in self.browse(cr, uid, ids):
            res[rec.id] = t_user_flag
        return res

    def _check_user_accounting(self, cr, uid, ids, field_name,
                               arg, context=None):

        user_obj = self.pool.get('res.users')
        t_user = user_obj.browse(cr, uid, uid)
        t_user_group_ids = t_user.groups_id
        t_user_flag = False

        for t_group in t_user_group_ids:
            if (t_group.category_id
             and (t_group.category_id.name == 'Accounting'
                  or t_group.category_id.name == 'Accounting & Finance')):
                t_user_flag = True
        res = {}
        for rec in self.browse(cr, uid, ids):
            res[rec.id] = t_user_flag
        return res

    def _get_persons_units_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}

        partners_data = self.browse(cr, uid, ids, context=context)
        for partner_data in partners_data:
            person_list = []
            if partner_data and partner_data.location_name_ids:
                for location_data in partner_data.location_name_ids:
                    for unit_data in location_data.units_ids:
                        for person_data in unit_data.persons_ids:
                            if person_data.partner_id.id not in person_list:
                                person_list.append(person_data.partner_id.id)
            result[partner_data.id] = person_list
        return result

    def get_fullname(self, name, surname):
        LETTERE = 'abcdefghijklmnopqrstuvwxyz'
        t_fullname_wsp = ((name + surname).lower()).strip()
        t_fullname = t_fullname_wsp.replace(" ", "")
        t_fullname = t_fullname.replace(u"à", "a")
        t_fullname = t_fullname.replace(u"è", "e")
        t_fullname = t_fullname.replace(u"é", "e")
        t_fullname = t_fullname.replace(u"ì", "i")
        t_fullname = t_fullname.replace(u"ò", "o")
        t_fullname = t_fullname.replace(u"ù", "u")
        for c in t_fullname:
            if c not in LETTERE:
                t_fullname = t_fullname.replace(c, "")
        return t_fullname

    def onchange_person_name(self, cr, uid, ids, t_name, t_surname, context=None):
        if not t_name or not t_surname:
            return {}

        warning = {}
        t_has_unaccent = registry.RegistryManager.get(cr.dbname).has_unaccent

        LETTERE = 'abcdefghijklmnopqrstuvwxyz'
        t_fullname = self.get_fullname(t_name, t_surname)

        t_sql = 'select count(*) \
                 from res_partner p '
        if t_has_unaccent:
            t_sql = t_sql + 'where translate(lower(unaccent(p.person_name || p.person_surname)), translate(lower(unaccent(p.person_name || p.person_surname)), ' + "'" + LETTERE + "'" + ',' + "''" + '),' + "''" + ') = ' + "'" + t_fullname + "'" 
        else:
            t_sql = t_sql + 'where translate(lower(p.person_name || p.person_surname), translate(lower(p.person_name || p.person_surname), ' + "'" + LETTERE + "'" + ',' + "''" + '),' + "''" + ') = ' + "'" + t_fullname + "'" 

        cr.execute(t_sql)
        t_dict = cr.dictfetchall()
        value = int(t_dict[0]['count'])
        if value > 0:
            warning = {
                'title': _('Attenzione!'),
                'message': _("Esiste già un'altra persona fisica con lo stesso nome e cognome. Può darsi che sia già stata inserita nel database! Questo è solo un avviso, puoi comunque proseguire con il salvataggio.")
            }

        if warning:
            return {'value': {},
                    'warning': warning,
                    }

        return {}

    def _get_role(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_data in self.browse(cr, uid, ids, context):
            res[t_data.id] = {'has_role': False,
                              'is_inspector': False,
                              'is_technical_officer': False,
                              'is_supervisor': False,
                              'is_inspector_system': False,
                              'is_relator': False,
                              'is_correlator': False,
                              'is_evaluator': False,
                              'is_direction_repr': False,
                              'is_observer': False,
                              'is_technical_expert': False,
                              'is_resp_group_inspection': False,
                              'is_assistant_inspection': False,
                              'is_department_director': False,
                              'is_secretary_management': False,
                              'is_candidate': False,
                              }
            for t_role in t_data.roles_ids:
                res[t_data.id]['has_role'] = True
                if t_role.role_id.inspector:
                    res[t_data.id]['is_inspector'] = True
                    break
                if t_role.role_id.technical_officer:
                    res[t_data.id]['is_technical_officer'] = True
                    break
                if t_role.role_id.supervisor:
                    res[t_data.id]['is_supervisor'] = True
                    break
                if t_role.role_id.inspector_system:
                    res[t_data.id]['is_inspector_system'] = True
                    break
                if t_role.role_id.relator:
                    res[t_data.id]['is_relator'] = True
                    break
                if t_role.role_id.correlator:
                    res[t_data.id]['is_correlator'] = True
                    break
                if t_role.role_id.evaluator:
                    res[t_data.id]['is_evaluator'] = True
                    break
                if t_role.role_id.direction_repr:
                    res[t_data.id]['is_direction_repr'] = True
                    break
                if t_role.role_id.observer:
                    res[t_data.id]['is_observer'] = True
                    break
                if t_role.role_id.technical_expert:
                    res[t_data.id]['is_technical_expert'] = True
                    break
                if t_role.role_id.resp_group_inspection:
                    res[t_data.id]['is_resp_group_inspection'] = True
                    break
                if t_role.role_id.assistant_inspection:
                    res[t_data.id]['is_assistant_inspection'] = True
                    break
                if t_role.role_id.department_director:
                    res[t_data.id]['is_department_director'] = True
                    break
                if t_role.role_id.secretary_management:
                    res[t_data.id]['is_secretary_management'] = True
                    break
                if t_role.role_id.candidate:
                    res[t_data.id]['is_candidate'] = True
                    break
        return res

    def _get_role_search(self, cr, uid, obj, name, args, context=None):

        t_name = name[3:]

        query = '''
            select
                accreditation_person_roles.partner_id
            from
                accreditation_person_roles
                join accreditation_roles
                     on accreditation_person_roles.role_id = accreditation_roles.id
            '''
        if name != 'has_role':
            query += '''
                where
                    accreditation_roles.''' + t_name + ''' = true

                '''
        cr.execute(query)
        res = cr.fetchall()
        ids = [('id', 'in', map(lambda x: x[0], res))]
        return ids

    def _get_birthdate(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):

            res[partner.id] = None
            if partner.birth_date:
                res[partner.id] = partner.birth_date

        return res

    def _get_main_units_ids(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        for partner_data in self.browse(cr, uid, ids, context=context):
            res[partner_data.id] = []
            for location_data in partner_data.location_name_ids:
                for unit_data in location_data.units_ids:
                    if unit_data.unit_category_id and unit_data.unit_category_id.is_main:
                        res[partner_data.id].append(unit_data.id)
        return res

    _columns = {
        # Denominazione Legale
        'name': fields.char('Denominazione Legale',
                            size=512,
                            select=True),

        # nome e cognome per persona fisica
        'partner_name': fields.related('name',
                                       type='char',
                                       relation='res.partner',
                                       string='Nome e Cognome',
                                       readonly=1),
        # Denominazione Abbreviata
        'entity_name': fields.char('Entity Name',
                                   size=512),
        # Sigla
        'entity_nick': fields.char('Entity Nick',
                                   size=64),
        # Codice Gamma
        'gamma_code': fields.char('Codice Gamma',
                                  size=10),
        'is_entity': fields.boolean('Entity',
                                    help="Check this box if this partner is an Entity."),

        'is_institution': fields.boolean('Institution',
                                         help="Check this box if this partner is an Institution."),

        # Riconoscimento diverso da ACCREDIA
        'different_than_accredia': fields.boolean('Riconoscimento diverso da ACCREDIA',
                                                  help="Riconoscimento diverso da ACCREDIA"),
        'ref_entity': fields.many2one('res.partner',
                                      'Ente di riferimento',
                                      domain=[('is_entity', '=', True)]),
        'reminder_state': fields.selection([('1', "Protocollo d'intesa"),
                                            ('2', 'Accordo diretto')],
                                           'Tipo Riconoscimento'),
        'obtained': fields.boolean('Accreditamento/Riconoscimento ottenuto'),

        # Categoria
        'entity_category_id': fields.many2many('accreditation.entity.categories',
                                               id1='partner_id',
                                               id2='entity_category_id',
                                               string='Categoria'),
        # Lista Sedi
        'location_name_ids': fields.one2many('accreditation.locations',
                                             'partner_id',
                                             'Location Lines'),
        'main_units_ids': fields.function(_get_main_units_ids, method=True, type='one2many', relation='accreditation.units', string='Unità Principali'),

        # Dipartimento
        'department_id': fields.many2one('hr.department',
                                         'Dipartimento'),

        # relazione (persons->entities) many2many
        # Persone fisiche con incompatibilità
        'persons_ids': fields.one2many('accreditation.persons.entities',
                                       'entity_id',
                                       'Persone Fisiche con Incompatibilità'),

        'member_ids': fields.one2many('accreditation.institution.members',
                                      'parent_id',
                                      'Componenti dei Comitati'),

        'persons_units_ids': fields.function(_get_persons_units_ids,
                                             relation='res.partner',
                                             type='one2many',
                                             string="Persone Fisiche relative alle Unità",
                                             readonly=True),

        'replaced_by_id': fields.function(_get_replaced_by,
                                          type="many2one",
                                          relation="res.partner",
                                          string="Replaced By"),
        'validity_date': fields.function(_get_validity_date,
                                         type="date",
                                         relation="res.partner",
                                         string="Data Validità"),
        'replaces_id': fields.function(_get_replaces,
                                       type="many2one",
                                       relation="res.partner",
                                       string="Replaces"),
        'property_account_receivable_code': fields.function(_get_property_account_receivable_code,
                                                            type="char",
                                                            relation="res.partner",
                                                            string="Codice Contabile"),
        'entity_changed': fields.boolean('Entity Changed'),
        'account_tax_id': fields.many2one('account.tax',
                                          'Prevalent Vat Code'),

        'accreditation_date': fields.date('Accreditation Date'),
        'accreditation_expiry_date': fields.date('Accreditation Expiry Date'),

        # reminder temporary fields
        'reminder_accrediting_entity': fields.many2one('res.partner',
                                                       'Reminder Accrediting Entity'),
        'reminder_audit_status': fields.char('Audit Status',
                                             size=1),
        'reminder_avowal_type': fields.char('Avowal Type',
                                            size=1),
        'admin_user_flag': fields.function(_check_user_admin,
                                           type="boolean",
                                           string="Super User"),
        'accounting_user_flag': fields.function(_check_user_accounting,
                                                type="boolean",
                                                string="Super User"),

        'km_rate': fields.float('KM Rate'),

        # ogni persona puo avere una o piu qualifiche
        'qualification_ids': fields.many2many('accreditation.qualifications',
                                              rel="accreditation_persons_qualifications_rel",
                                              id1='partner_id',
                                              id2='qualification_id',
                                              string='Qualifiche'),

        'magnitude': fields.char('Grandezza di riferimento',
                                 size=80),
        'source_system': fields.char('Source System',
                                     size=5),
        'code': fields.char('Code',
                            size=10),
        # ruoli
        'roles_ids': fields.one2many('accreditation.person.roles',
                                     'partner_id',
                                     'Ruoli'),

        'has_role': fields.function(_get_role, fnct_search=_get_role_search,
                                    string="Ha un Ruolo", type='boolean', multi='roles'),
        'is_inspector': fields.function(_get_role, fnct_search=_get_role_search,
                                        string="E' Ispettore Tecnico", type='boolean', multi='roles'),
        'is_technical_officer': fields.function(_get_role, fnct_search=_get_role_search,
                                                string="E' Technical Officer", type='boolean', multi='roles'),
        'is_supervisor': fields.function(_get_role, fnct_search=_get_role_search,
                                         string="E' Supervisor", type='boolean', multi='roles'),
        'is_inspector_system': fields.function(_get_role, fnct_search=_get_role_search,
                                               string="E' Ispettore di sistema", type='boolean', multi='roles'),
        'is_relator': fields.function(_get_role, fnct_search=_get_role_search,
                                      string="E' Relatore", type='boolean', multi='roles'),
        'is_correlator': fields.function(_get_role, fnct_search=_get_role_search,
                                         string="E' Correlatore", type='boolean', multi='roles'),
        'is_evaluator': fields.function(_get_role, fnct_search=_get_role_search,
                                        string="E' Evaluator", type='boolean', multi='roles'),
        'is_direction_repr': fields.function(_get_role, fnct_search=_get_role_search,
                                             string="E' Rappresentante della direzione",
                                             type='boolean', multi='roles'),
        'is_observer': fields.function(_get_role, fnct_search=_get_role_search,
                                       string="E' Osservatore", type='boolean', multi='roles'),
        'is_technical_expert': fields.function(_get_role, fnct_search=_get_role_search,
                                               string="E' Esperto tecnico",
                                               type='boolean', multi='roles'),
        'is_resp_group_inspection': fields.function(_get_role, fnct_search=_get_role_search,
                                                    string="E' Responsabile Gruppo Verifica Ispettiva",
                                                    type='boolean', multi='roles'),
        'is_assistant_inspection': fields.function(_get_role, fnct_search=_get_role_search,
                                                   string="E' Assistente Verifica Ispettiva",
                                                   type='boolean', multi='roles'),
        'is_department_director': fields.function(_get_role, fnct_search=_get_role_search,
                                                  string="E' Direttore Di Dipartimento",
                                                  type='boolean', multi='roles'),
        'is_secretary_management': fields.function(_get_role, fnct_search=_get_role_search,
                                                   string="E' Segreteria/Amministrazione",
                                                   type='boolean', multi='roles'),
        'is_candidate': fields.function(_get_role, fnct_search=_get_role_search,
                                        string="E' Candidato", type='boolean', multi='roles'),

        # ogni persona puo essere in relazione con uno o piu enti (se incompatibile)
        'partner_ids': fields.one2many('accreditation.persons.entities',
                                       'partner_id',
                                       'Enti Incompatibili'),

        # ogni person puo avere una o piu unit -> one2many
        'unit_ids': fields.one2many('accreditation.persons.units',
                                    'partner_id',
                                    'Related Units'),
        # ogni persona puo avere uno o piu indirizzi
        # che derivano dalle Unità
        'address_units_ids': fields.related('unit_ids',
                                            relation='accreditation.persons.units',
                                            type='one2many',
                                            string='Unit related addresses',
                                            readonly=True),

        'employee_pa': fields.boolean('Dipendente P.A.'),

        # override existing fields (hide from advanced search)
        'birthdate': fields.function(_get_birthdate,
                                     type='date',
                                     string="Hidden",
                                     store=False),

        # campi di appoggio per risolvere problemi alle viste
        'attr_individual': fields.related('individual',
                                          type='boolean',
                                          string='Individual',
                                          readonly=True),
        'attr_accounting_user_flag': fields.related('accounting_user_flag',
                                                    type='boolean',
                                                    string='Super User',
                                                    readonly=True),
        'attr_admin_user_flag': fields.related('admin_user_flag',
                                               type='boolean',
                                               string='Super User',
                                               readonly=True),
        'attr_is_entity': fields.related('is_entity',
                                         type='boolean',
                                         string='Ente',
                                         readonly=True),
        'attr_id': fields.related('id',
                                  type='integer',
                                  string='ID',
                                  readonly=True),

        }

    _defaults = {
        'is_company': True,
        'entity_changed': False,
        'sex': None,
    }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.individual and record.person_name and record.person_surname:
                name = record.person_name + ' ' + record.person_surname
            if record.parent_id:
                name = "%s, %s" % (record.parent_name, name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res

    def copy(self, cr, uid, id, default=None, context=None):

        if context is None:
            context = {}
        ctx = context.copy()

        user_obj = self.pool.get('res.users')
        my_company = user_obj.browse(cr, uid, uid).company_id
        t_partner_data = self.browse(cr, uid, id, ctx)

        if(not my_company.subaccount_auto_generation_customer
           and 'property_account_receivable' not in default
           and t_partner_data.property_account_receivable):
            t_property_id = t_partner_data.property_account_receivable.id
            default.update({'property_account_receivable': t_property_id})

        if(not my_company.subaccount_auto_generation_supplier
           and 'property_account_payable' not in default
           and t_partner_data.property_account_payable):
            t_property_id = t_partner_data.property_account_payable.id
            default.update({'property_account_payable': t_property_id})

        data = super(res_partner_accredia, self).copy_data(cr, uid, id, default, ctx)
        if 'bank_ids' in data:
            del data['bank_ids']
        if 'child_ids' in data:
            del data['child_ids']
        if 'contract_ids' in data:
            del data['contract_ids']
        if 'invoice_ids' in data:
            del data['invoice_ids']
        if 'user_ids' in data:
            del data['user_ids']
        new_id = super(res_partner_accredia, self).create(cr, uid, data, ctx)
        self.copy_translations(cr, uid, id, new_id, ctx)
        return new_id

    def _get_receivable_default_code(self, cr, uid, ids, parent_id):
        if not parent_id:
            return {}

        account_obj = self.pool.get('account.account')
        t_entity = self.browse(cr, uid, parent_id, context=None)
        t_acc_data = t_entity.property_account_receivable
        max_code = None
        if t_acc_data:
            max_code = account_obj.get_max_code(cr, uid, ids, t_acc_data.id)
        return max_code

    def _get_payable_default_code(self, cr, uid, ids, parent_id):
        if not parent_id:
            return {}

        account_obj = self.pool.get('account.account')
        t_entity = self.browse(cr, uid, parent_id, context=None)
        t_acc_data = t_entity.property_account_payable
        max_code = None
        if t_acc_data:
            max_code = account_obj.get_max_code(cr, uid, ids, t_acc_data.id)
        return max_code

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        t_view_person = context.get('view_person', False)
        if t_view_person:
            vals['individual'] = True
            vals['is_company'] = False

        if 'fiscalcode' in vals:
            t_fiscal = vals['fiscalcode']
            # TODO
            person_ids = self.search(cr, uid, [('fiscalcode', 'like', t_fiscal)], limit=1)
            if person_ids:
                raise orm.except_orm(_('Error'),
                                     _('This fiscal code already exists in the database. Maybe this person was already inserted! Please Check!'))

        if 'parent_id' not in vals and 'individual' in vals and vals['individual'] and ('person_name' not in vals or not vals['person_name'] or 'person_surname' not in vals or not vals['person_surname']):
            raise orm.except_orm(_('Error'),
                                 _('Name and Surname are mandatory!'))

        if 'individual' in vals and vals['individual'] and 'person_name' in vals and vals['person_name'] and 'person_surname' in vals and vals['person_surname']:
            vals['name'] = vals['person_name'] + ' ' + vals['person_surname']

        # step2
#        if 'parent_id' in vals and vals['parent_id'] and 'individual' in vals and vals['individual']:
#            t_parent_data = self.browse(cr, uid, vals['parent_id'], context=None)
#            vals['person_surname'] = t_parent_data.person_surname
#            vals['person_name'] = t_parent_data.person_name

        res = super(res_partner_accredia, self).create(cr, uid, vals, context)

        return res

    def write(self, cr, uid, ids, vals, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        for data in self.browse(cr, uid, ids):

            t_parent = data.parent_id and True or False
            t_individual = data.individual or False
            t_is_entity = data.is_entity or False
            t_person_name = data.person_name or ''
            t_person_surname = data.person_surname or ''
            t_name = data.name or ''

            if 'individual' in vals and vals['individual']:
                t_individual = vals['individual']
            if 'is_entity' in vals and vals['is_entity']:
                t_is_entity = vals['is_entity']
            if 'person_name' in vals and vals['person_name']:
                t_person_name = vals['person_name']
            if 'person_surname' in vals and vals['person_surname']:
                t_person_surname = vals['person_surname']
            if 'name' in vals and vals['name']:
                t_name = vals['name']

            if t_individual and t_parent:
                if t_person_name or t_person_surname:
                    raise orm.except_orm(_('Error'),
                                         _('Non è possibile cambiare il nome o il cognome di una persona fisica direttamente da un suo contatto!'))

            if t_name and t_is_entity:
                vals['entity_name'] = t_name

            if t_individual and not t_parent:
                if t_person_name and t_person_surname:
                    vals['name'] = t_person_name + ' ' + t_person_surname

        res = super(res_partner_accredia, self).write(cr, uid, ids, vals, context=context)

        return res
