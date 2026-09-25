# -*- coding: utf-8 -*-

{
    'name': 'Fire Evacuation',
    'category': 'Human Resources/reception',
    'description': 'Fire Evacuation',
    'summary': 'Fire Evacuation system.',
    'description': '''
Fire Evacuation
===============

    Fire Evacuation system.

    Features:

        - Web integration: Exposes HTTP endpoints for external systems.
        - UI Integration: Extends 2 view(s) in the Odoo interface.
        - Extends Odoo: Builds on fire.evacuation, fire.evacuation.line.
    ''',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-reception/fire_evacuation',
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
    'version': '18.0.1.0.0',
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
