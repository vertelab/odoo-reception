# -*- coding: utf-8 -*-

{
    'name': 'Fire Evacuation',
    'category': 'Human Resources/reception',
    'description': 'Fire Evacuation',
    'summary': 'Fire Evacuation system',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-reception/fire_evacuation',
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
    'version': '1.0',
    'depends': [
        'visitor_management',
        'hr_attendance',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fire_evacuation_views.xml',
        'views/templates.xml',
    ],
}
