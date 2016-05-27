# -*- coding: utf-8 -*-
{
    'name': "binary_field_extend",

    'summary': """
        Modifica la visualizzazione del campo per eseguire l'upload""",

    'description': """
        Modifica la visualizzazione del campo per eseguire l'upload.
    """,

    'author': "Isa s.r.l.",
    'website': "http://www.isa.it",

    'category': 'web',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'web'
    ],

    'qweb': [
        'static/src/xml/templates.xml',
    ],
}
