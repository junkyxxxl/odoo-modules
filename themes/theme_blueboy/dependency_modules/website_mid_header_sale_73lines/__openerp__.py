# -*- coding: utf-8 -*-
##############################################################################
#
#    73Lines Development Pvt. Ltd.
#    Copyright (C) 2009-TODAY 73Lines(<http://www.73lines.com>).
#
#    you can modify it under the terms of the GNU LESSER 
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies 
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE 
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.  
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Website Mid Header for Sale By 73Lines',
    'description': 'website Mid Header for Sale',
    'category': 'Website',
    'version':'1.2',
    'author': '73Lines',
    'depends': ['website','website_sale','website_mid_header_73lines','auth_signup','website_language_flag_73lines','website_portal'],
    'data': [
        'views/assets.xml',
        'views/s_search_box.xml',
        'views/website_mid_header_sale_template.xml',
        ],
    'images': [
        'static/description/website_mid_header_sale.jpg',    
    ],
    'price': 40,
#     'license': 'OEEL-1',
    'currency': 'EUR',
}