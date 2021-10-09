# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class BookingsReport(models.TransientModel):
    _name = "product.booking.report"
    _description = "Bookings Reports"

    booking_event = fields.Many2one('product.booking.event', string="Evento")
    customer = fields.Many2one('res.partner', string="Cliente", domain=[('customer', '=', True)])
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

    def _build_contexts(self, data):
        return {
            'booking_event':    'booking_event' in data['form'] and data['form']['booking_event'] or False,
            'customer':         'customer' in data['form'] and data['form']['customer'] or False,
            'date_from':        data['form']['date_from'] or False,
            'date_to':          data['form']['date_to'] or False
        }

    def _print_report(self, data):
        return self.env.ref('product_booking.action_report_booking').report_action(self, data=data, config=False)
