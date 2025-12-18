from odoo import http
from odoo.http import request
from datetime import datetime


class FireEvacuationController(http.Controller):

    @http.route('/fire/evacuation', type='http', auth='user', website=True)
    def evacuation_index(self, **kwargs):
        # Check for ongoing evacuation
        evacuation = request.env['fire.evacuation'].search([
            ('state', '=', 'ongoing')
        ], limit=1, order='date desc')

        if evacuation:
            # Redirect to existing evacuation
            return request.redirect(f'/fire/evacuation/{evacuation.id}')

        # Show start button
        return request.render('fire_evacuation.start_evacuation', {})

    @http.route('/fire/evacuation/start', type='http', auth='user', website=True, csrf=True)
    def start_evacuation(self, **kwargs):

        # Create new evacuation
        evacuation = request.env['fire.evacuation'].create({
            'name': f'Evacuation {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'date': datetime.now(),
            'state': 'ongoing',
        })

        # Load people
        evacuation.action_load_people()

        return request.redirect(f'/fire/evacuation/{evacuation.id}')

    @http.route('/fire/evacuation/<int:evacuation_id>', type='http', auth='user', website=True)
    def view_evacuation_list(self, evacuation_id, **kwargs):
        evacuation = request.env['fire.evacuation'].browse(evacuation_id)

        if not evacuation.exists():
            return request.redirect('/fire/evacuation')

        return request.render('fire_evacuation.evacuation_list_template', {
            'evacuation': evacuation,
            'lines': evacuation.fire_evacuation_ids,
        })

    @http.route('/fire/evacuation/<int:evacuation_id>/reload', type='http', auth='user', website=True)
    def reload_evacuation_lines(self, evacuation_id, **kwargs):
        evacuation = request.env['fire.evacuation'].browse(evacuation_id)

        if evacuation.exists():
            evacuation.action_reload_lines()

        return request.redirect(f'/fire/evacuation/{evacuation_id}')

    @http.route('/fire/evacuation/<int:line_id>/toggle', type='http', auth='user', website=True)
    def toggle_person_ok(self, line_id, **kwargs):
        line = request.env['fire.evacuation.line'].browse(line_id)

        if line.exists():
            line.write({'is_ok': not line.is_ok})
            return request.redirect(f'/fire/evacuation/{line.fire_evacuation_id.id}')

        return request.redirect('/fire/evacuation')

    @http.route('/fire/evacuation/<int:evacuation_id>/complete', type='http', auth='user', website=True)
    def complete_evacuation(self, evacuation_id, **kwargs):
        evacuation = request.env['fire.evacuation'].browse(evacuation_id)

        if evacuation.exists():
            evacuation.write({'state': 'completed'})

        return request.redirect('/fire/evacuation')