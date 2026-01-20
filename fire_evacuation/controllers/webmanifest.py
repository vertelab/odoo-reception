# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from odoo import http
from odoo.http import request
from odoo.tools.misc import file_open
from odoo.tools.translate import _
from odoo.addons.web.controllers.webmanifest import WebManifest


class WebManifestExtended(WebManifest):

    def _get_webmanifest(self):
        web_app_name = request.env['ir.config_parameter'].sudo().get_param('web.web_app_name', 'Fire Evacuation')
        manifest = {
            'name': web_app_name,
            'short_name': web_app_name,
            'description': web_app_name,
            'scope': '/fire/evacuation/new',
            'start_url': '/fire/evacuation/new',
            'display': 'standalone',
            'background_color': '#ffffff',
            'theme_color': '#875A7B',
        }
        # icon_sizes = ['192x192', '512x512']
        icon_sizes = ['192', '512']
        manifest['icons'] = [{
            'src': '/fire_evacuation/static/src/img/icon-%s.png' % size,
            'sizes': size,
            'type': 'image/png',
        } for size in icon_sizes]
        manifest['shortcuts'] = self._get_shortcuts()
        return manifest



