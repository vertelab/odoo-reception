# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from odoo.tools import consteq
import logging

_logger = logging.getLogger(__name__)

class reception(http.Controller):
    def _get_additional_info(self, reception, lang, is_mobile=False):
        _logger.warning(f"_get_additional_info {reception} {lang}")
        res = request.render('visitor_management.reception', {
            'reception': reception,
            'is_mobile': is_mobile,
            'current_lang': lang,
        })
        _logger.warning(f"Rendered {res}")
        return res

    def _verify_token(self, reception, token):
        if consteq(reception.access_token, token):
            return True
        else:
            time_difference = fields.Datetime.now() - fields.Datetime.from_string(token[-19:])
            if time_difference.total_seconds() <= 3600 and consteq(reception._get_tmp_code(), token[:64]):
                return True
            return False

    @http.route('/kiosk/<int:reception_id>/<string:token>', type='http', auth='public', website=True)
    def launch_reception(self, reception_id, token, lang=False):
        _logger.warning(f"Hello {reception_id} {token}")

        reception = request.env['reception.reception'].sudo().browse(reception_id)
        
        if request.env.uid and not lang:
            lang = request.env.user.lang

        # return request.render('visitor_management.reception', {
        #     'reception': reception,
        #     'is_mobile': False,
        #     'current_lang': 'en_US',
        # })
        # _logger.warning(f"Rendered {res}")
        
        
        if not reception.exists() or not self._verify_token(reception, token):
            _logger.warning(f"Not found {reception_id} {token}")
            return request.not_found()
        return self._get_additional_info(reception, lang)

    @http.route('/kiosk/<int:reception_id>/mobile/<string:token>', type='http', auth='public', website=True)
    def launch_reception_mobile(self, reception_id, token, lang='en_US'):
        reception = request.env['reception.reception'].sudo().browse(reception_id)
        if not reception.exists() or not self._verify_token(reception, token):
            return request.render('visitor_management.reception_qr_expired')
        return self._get_additional_info(reception, lang, is_mobile=True)

    @http.route('/kiosk/<int:reception_id>/get_tmp_code/<string:token>', type='json', auth='public')
    def get_tmp_code(self, reception_id, token):
        reception = request.env['reception.reception'].sudo().browse(reception_id)
        if not reception.exists() or not self._verify_token(reception, token):
            return request.not_found()
        return (reception._get_tmp_code(), fields.Datetime.to_string(fields.Datetime.now()))

    @http.route('/visitor/<int:reception_id>/<string:token>/get_reception_data', type='json', auth='public')
    def get_reception_data(self, reception_id, token):
        reception = request.env['reception.reception'].sudo().browse(reception_id)
        _logger.warning(f"get_reception_data {reception_id}")
        _logger.warning(f"get_reception_data {reception._get_reception_data()}")
        if not reception.exists() or not self._verify_token(reception, token):
            return request.not_found()
        return reception._get_reception_data()

    @http.route('/visitor/<int:reception_id>/<string:token>/get_planned_visitors', type='json', auth='public')
    def get_planned_visitors(self, reception_id, token):
        reception = request.env['reception.reception'].sudo().browse(reception_id)
        if not reception.exists() or not self._verify_token(reception, token):
            return request.not_found()
        return reception._get_planned_visitors()

    @http.route('/visitor/<int:reception_id>/background', type='http', auth='public')
    def reception_background_image(self, reception_id):
        reception = request.env['reception.reception'].sudo().browse(reception_id)
        if not reception.image:
            return ""
        return request.env['ir.binary']._get_image_stream_from(reception, 'image').get_response()

    @http.route('/visitor/<int:reception_id>/<string:token>/get_hosts', type='json', auth='public')
    def get_hosts(self, reception_id, token, name):
        reception = request.env['reception.reception'].sudo().browse(reception_id)
        if not reception.exists() or not self._verify_token(reception, token):
            return request.not_found()
        return request.env['hr.employee'].sudo().name_search(name, [('user_id', '!=', False), ('company_id', '=', reception.company_id.id)])

    @http.route('/visitor/<int:reception_id>/<string:token>/prepare_visitor_data', type='json', auth='public', methods=['POST'])
    def prepare_visitor_data(self, reception_id, token, visitor_id=None, **kwargs):
        reception = request.env['reception.reception'].sudo().browse(reception_id)
        _logger.warning(f"perpare_visitor_data {reception_id}")
        
        if not reception.exists() or not self._verify_token(reception, token):
            return request.not_found()
        visitor = request.env['reception.visitor'].browse(visitor_id)
        _logger.warning(f"perpare_visitor_data {visitor}")
        vals = {'state': 'checked_in'}
        if visitor:
            return visitor.sudo().write(vals)
        else:
            vals.update({
                'station_id': reception.id,
                'name': kwargs.get('name'),
                'phone': kwargs.get('phone'),
                'email': kwargs.get('email'),
                'check_in': fields.Datetime.now(),
                'company': kwargs.get('company'),
                'host_ids': [(4, host_id) for host_id in kwargs.get('host_ids')],
            })
            visitor = request.env['reception.visitor'].sudo().create(vals)
            visitor._notify()
            return {'visitor_id': visitor.id}
