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

from openerp import fields, models, api


class HrDepartment(models.Model):

    _inherit = "hr.department"

    department_nick = fields.Char('Department Nick', size=64)
    project_sequence_id = fields.Many2one('ir.sequence', 'Project sequence', help='Entry project sequence')
    manage_purchase_requisition = fields.Boolean('Manage Purchase Requisition')
    analytic_account_for_invoicing = fields.Char('Analytic Account for Invoicing', size=2)
    gamma_code = fields.Char('Gamma Code', size=10)
    user_ids = fields.Many2many(comodel_name='res.users',
                                column1='user_id',
                                column2='department_id',
                                string='Utenti')
    enable_tab_sectors = fields.Boolean('Abilita Tab Settori')
    enable_tab_tests = fields.Boolean('Abilita Tab Prove Accreditate')
    experimental_journal_id = fields.Many2one('account.analytic.journal',
                                              'Sezionale accertamenti sperimentali',
                                              help='Sezionale accertamenti sperimentali')

    enable_filter_standard_id = fields.Boolean(string='Abilita Filtro Norma')

    @api.multi
    @api.depends('department_nick', 'name')
    def name_get(self):
        res = []
        for record in self:
            descr = (record.department_nick or '')
            if record.name:
                descr += ' (' + (record.name or '') + ')'
            res.append((record.id, descr))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        search_uid = [self._uid]

        if self._context.get('t_user_id', False):
            t_user_id = self._context.get('t_user_id', False)
            search_uid = [t_user_id]

        ctx_obj = self._context.get('t_obj', False)

        if name and ctx_obj:
            t_args = args[0] and args[0][2] and args[0][2][0] and args[0][2][0][2] or []
            args = [('user_ids', 'in', search_uid),
                    ('id', 'in', t_args),
                    '|',
                    ('department_nick', operator, name),
                    ('name', operator, name)]
        elif name:
            args = [('user_ids', 'in', search_uid),
                    '|',
                    ('department_nick', operator, name),
                    ('name', operator, name)]
        elif ctx_obj:
            t_args = args[0] and args[0][2] and args[0][2][0] and args[0][2][0][2] or []
            args = [('user_ids', 'in', search_uid),
                    ('id', 'in', t_args)]
        else:
            args = [('user_ids', 'in', search_uid)]

        return super(HrDepartment, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
