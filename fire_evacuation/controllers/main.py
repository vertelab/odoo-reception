from odoo import http
from odoo.http import request
from datetime import datetime


class FireEvacuationController(http.Controller):

    @http.route('/fire/evacuation/new', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=True)
    def new_evacuation(self, **post):
        if request.httprequest.method == 'POST':
            site = post.get('site')

            if not site:
                return request.render('fire_evacuation.new_evacuation_form', {
                    'error': 'Site name is required'
                })

            evacuation = request.env['fire.evacuation'].sudo().create({
                'name': site,
                'date': datetime.now(),
            })

            evacuation.action_aggregate()

            return request.redirect(f'/fire/evacuation/{evacuation.id}')

        return request.render('fire_evacuation.new_evacuation_form', {})

    @http.route('/fire/evacuation/<int:evacuation_id>', type='http', auth='user', website=True)
    def view_evacuation_list(self, evacuation_id, **kwargs):
        evacuation = request.env['fire.evacuation'].browse(evacuation_id)

        if not evacuation.exists():
            return request.render('website.404')

        return request.render('fire_evacuation.evacuation_list_template', {
            'evacuation': evacuation,
            'lines': evacuation.fire_evacuation_ids,
        })

    @http.route('/fire/evacuation/<int:evacuation_id>/reload', type='http', auth='user', website=True)
    def reload_evacuation_people(self, evacuation_id, **kwargs):
        evacuation = request.env['fire.evacuation'].browse(evacuation_id)

        if evacuation.exists():
            evacuation.action_aggregate()

        return request.redirect(f'/fire/evacuation/{evacuation_id}')

    @http.route('/fire/evacuation/<int:line_id>/toggle', type='http', auth='user', website=True)
    def toggle_person_ok(self, line_id, **kwargs):
        line = request.env['fire.evacuation.line'].browse(line_id)

        if line.exists():
            line.write({'is_ok': not line.is_ok})
            return request.redirect(f'/fire/evacuation/{line.fire_evacuation_id.id}')

        return request.redirect('/fire/evacuation/new')