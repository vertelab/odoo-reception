from odoo import models, fields, api, _


class FireEvacuation(models.Model):
    _name = 'fire.evacuation'
    _description = 'Fire Evacuation'

    name = fields.Char(string='Site')
    date = fields.Datetime(string='Date')
    fire_evacuation_ids = fields.One2many('fire.evacuation.line', 'fire_evacuation_id', string="Fire Evacuations")

    def action_aggregate(self):
        self.ensure_one()

        # Clear existing lines
        self.fire_evacuation_ids.unlink()

        lines_to_create = []

        # Aggregate from all sources
        lines_to_create.extend(self._get_reception_visitors())
        lines_to_create.extend(self._get_employees())

        # Create all lines
        self.env['fire.evacuation.line'].create(lines_to_create)

        return True

    def _get_reception_visitors(self):
        lines = []

        visitors = self.env['reception.visitor'].search([
            ('state', '=', 'checked_in')  # Adjust state condition as needed
        ])

        for visitor in visitors:
            lines.append({
                'name': visitor.name,
                'phone': visitor.phone,
                'res_model': 'reception.visitor',
                'res_id': visitor.id,
                'fire_evacuation_id': self.id,
            })

        return lines

    def _get_employees(self):
        lines = []

        attendances = self.env['hr.attendance'].search([
            ('check_out', '=', False),  # Still checked in
            # Add site filter if available
        ])

        for attendance in attendances:
            lines.append({
                'name': attendance.employee_id.name,
                'phone': attendance.employee_id.work_phone or attendance.employee_id.mobile_phone,
                'res_model': 'hr.attendance',
                'res_id': attendance.id,
                'fire_evacuation_id': self.id,
            })

        return lines

class FireEvacuationLine(models.Model):
    _name = 'fire.evacuation.line'
    _description = 'Fire Evacuation Line'

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    name = fields.Char(string='Name')
    phone = fields.Char(string='Phone Number')

    is_ok = fields.Boolean(default=False, string='Is OK?')

    res_model = fields.Char('Related Document Model', required=True)
    res_id = fields.Integer('Related Document ID', required=True)
    resource_ref = fields.Reference('_selection_target_model', 'Source', compute='_compute_resource_ref')
    fire_evacuation_id = fields.Many2one('fire.evacuation', string='Fire Evacuation')

    @api.depends('res_model', 'res_id')
    def _compute_resource_ref(self):
        for line in self:
            if line.res_model and line.res_id:
                line.resource_ref = f"{line.res_model},{line.res_id}"
            else:
                line.resource_ref = False