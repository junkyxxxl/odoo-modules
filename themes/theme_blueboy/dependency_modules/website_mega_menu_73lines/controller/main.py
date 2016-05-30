# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
import werkzeug
import datetime
import time

from openerp.tools.translate import _


class website_mega_menu(http.Controller):

    @http.route(["/megamenu/edit/<model('website.menu'):menu>"], type='http', auth="user", website=True)
    def template_view(self, menu, **post):
        values = { 'template': menu }
        return request.website.render('website_mega_menu_73lines.menu_template', values)

