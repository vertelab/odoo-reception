# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import models, fields, api, tools, _
from werkzeug.urls import url_join
import uuid

ASK_FIELDS_SELECTION = [
    ("required", "Required"),
    ("optional", "Optional"),
    ("none", "None"),
]

PLANNED_VISITOR_TIME = 60

class reception(models.Model):
    _name = 'reception.reception'
    _description = 'Reception'

    access_token = fields.Char("Security Token", default=lambda self: str(uuid.uuid4()), required=True, copy=False, readonly=True)
    active = fields.Boolean(default=True)
    ask_company = fields.Selection(string='Organization', selection=ASK_FIELDS_SELECTION, default='optional', required=True)
    ask_email = fields.Selection(string='Email', selection=ASK_FIELDS_SELECTION, default='none', required=True)
    ask_phone = fields.Selection(string='Phone', selection=ASK_FIELDS_SELECTION, default='required', required=True)
    authenticate_guest = fields.Boolean('Authenticate Guest', default=True, groups='visitor_management.reception_group_user')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    description = fields.Html(groups='visitor_management.reception_group_user')
    guest_on_site = fields.Integer('Guests On Site', compute='_compute_dashboard_data')
    host_selection = fields.Boolean('Host Selection', groups='visitor_management.reception_group_user')
    image = fields.Image("Image")
    is_favorite = fields.Boolean()
    kiosk_url = fields.Char('Kiosk URL', compute='_compute_kiosk_url', groups='visitor_management.reception_group_user')
    latest_check_in = fields.Char(compute='_compute_dashboard_data')
    mail_template_id = fields.Many2one(comodel_name='mail.template',string='Email Template',domain="[('model', '=', 'reception.reception')]",default=lambda self: self.env.ref('visitor_management.reception_mail_template', raise_if_not_found=False))
    name = fields.Char('reception Name', required=True)
    notify_discuss = fields.Boolean('Notify by discuss', default=True, groups='visitor_management.reception_group_user')
    notify_email = fields.Boolean('Notify by email', groups='visitor_management.reception_group_user')
    notify_sms = fields.Boolean('Notify by SMS', groups='visitor_management.reception_group_user')
    pending = fields.Integer('Pending', compute='_compute_dashboard_data')
    responsible_ids = fields.Many2many('res.users', string='Responsibles', required=True)
    self_check_in = fields.Boolean('Self Check-In', groups='visitor_management.reception_group_user',help='Shows a QR code in the interface, for guests to check in from their mobile phone.')
    sms_template_id = fields.Many2one('sms.template',string='SMS Template',domain="[('model', '=', 'reception.reception')]",default=lambda self: self.env.ref('visitor_management.reception_sms_template', raise_if_not_found=False))
    theme = fields.Selection(selection=[("light", "Light"), ("dark", "Dark")], default='light')
    visitor_ids = fields.One2many('reception.visitor', 'station_id', string='Visitors')
    visitor_properties_definition = fields.PropertiesDefinition('Visitor Properties')

    def _compute_dashboard_data(self):
        """ This method computes the number of guests currently on site, the number of pending visitors and the time of the latest check-in. """
        visitor_data = self.env['reception.visitor']._read_group([
                ('state', 'in', ('checked_in', 'planned')),
                ('station_id', 'in', self.ids),
            ], ['station_id', 'state'], ['__count'])
        checked_in_mapped = {station.id: count for station, state, count in visitor_data if state == 'checked_in'}
        planned_mapped = {station.id: count for station, state, count in visitor_data if state == 'planned'}
        for reception in self:
            guest_on_site = pending = 0
            latest_check_in = False
            if reception.visitor_ids:
                guest_on_site = checked_in_mapped.get(reception.id, 0)
                pending = planned_mapped.get(reception.id, 0)
                last_visitors = reception.visitor_ids.filtered(lambda v: v.state == 'checked_in')
                latest_check_in_time = last_visitors and last_visitors[-1].check_in
                if latest_check_in_time:
                    total_seconds = (datetime.now() - latest_check_in_time).total_seconds()
                    time_diff = int(total_seconds / 60) if total_seconds < 3600 else int(total_seconds / 3600)
                    latest_check_in = _("Last Check-In: %s minutes ago", time_diff) if total_seconds < 3600 \
                        else _("Last Check-In: %s hours ago", time_diff)
            reception.update({
                'guest_on_site': guest_on_site,
                'pending': pending,
                'latest_check_in': latest_check_in,
            })

    @api.depends('access_token')
    def _compute_kiosk_url(self):
        for reception in self:
            reception.kiosk_url = url_join(reception.get_base_url(), '/kiosk/%s/%s' % (reception.id, reception.access_token))

    def action_open_kiosk(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.kiosk_url,
            'target': 'new',
        }

    def action_open_visitors(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Visitors"),
            'res_model': 'reception.visitor',
            'view_mode': 'list,form,kanban,graph,pivot,calendar',
            'context': {
                "search_default_state_is_planned": 1,
                "search_default_state_is_checked_in": 1,
                "search_default_today": 1
            },
            'domain': [('station_id.id', '=', self.id)],
        }

    def get_kiosk_url(self):
        return self.kiosk_url

    def _get_visitor_field(self):
        return ['description', 'host_selection', 'self_check_in', 'theme',
          'ask_email', 'ask_phone', 'ask_company', 'authenticate_guest']

    def _get_reception_data(self):
        """ Returns the data to the frontend. """
        self.ensure_one()
        data = {
            'company': {'name': self.company_id.name, 'id': self.company_id.id},
            'langs': [{'code': lang[0], 'name': lang[1]} for lang in self.env['res.lang'].get_installed()],
            'station': self.search_read([('id', '=', self.id)], self._get_visitor_field()),
        }
        return data

    def _get_planned_visitors(self):
        """ Returns the planned visitors for quick sign in to the frontend. """
        time_min = datetime.now() - timedelta(minutes=PLANNED_VISITOR_TIME)
        time_max = datetime.now() + timedelta(minutes=PLANNED_VISITOR_TIME)
        visitors = self.env['reception.visitor'].sudo().search_read(
                [('check_in', '>=', time_min), ('check_in', '<=', time_max), ('state', '=', 'planned'), ('station_id.id', '=', self.id)],
                ['name', 'company', 'message', 'host_ids'])
        if visitors:
            return [{
                **visitor,
                'host_ids': [{'id': host.id, 'name': host.name} for host in self.env['hr.employee'].browse(visitor['host_ids'])]
            } for visitor in visitors]
        return []

    def _get_tmp_code(self):
        self.ensure_one()
        return tools.hmac(self.env(su=True), 'kiosk-mobile', (self.id, fields.Date.to_string(fields.Datetime.now())))
