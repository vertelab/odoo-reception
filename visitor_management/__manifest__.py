# -*- coding: utf-8 -*-

{
    'name': 'Visitor Management',
    'category': 'Human Resources/reception',
    'description': 'A visitor management system that streamlines guest check-ins and check-outs while instantly notifying hosts.',
    'summary': 'Visitor management system',
    'author': 'Vertel AB',
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
    'version': '1.0',
    'depends': [
        'hr',
        'sms',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/visitor_report_views.xml',
        'views/visitor_views.xml',
        'views/reception_views.xml',
        'views/visitor_menus.xml',
        'views/visitor_templates.xml',
        'views/visitor_qr_expiration.xml',
        'data/mail_template_data.xml',
        'data/sms_template_data.xml',
        'data/visitor_data.xml',
        'data/visitor_templates.xml',
        'data/visitor_tour.xml',
    ],
    'demo': [
        'demo/visitor_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'visitor_management/static/src/js/**/*',
        ],
        'visitor_management.assets_visitor': [
            "visitor_management/static/src/primary_variables.scss",
            "visitor_management/static/src/bootstrap_overridden.scss",

            ("include", "web._assets_helpers"),
            ("include", "web._assets_frontend_helpers"),
            ("include", "web._assets_primary_variables"),
            "web/static/src/scss/pre_variables.scss",

            "web/static/lib/bootstrap/scss/_functions.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            'web/static/lib/bootstrap/scss/_variables-dark.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',
            ("include", "web._assets_bootstrap_frontend"),

            'web/static/lib/zxing-library/zxing-library.js',
            'visitor_management/static/src/**/*',
        ],
        'web.assets_tests': [
            'visitor_management/static/tests/tours/**/*',
        ],
    },
}
