# -*- coding: utf-8 -*-
import logging

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
                                 copy=True, auto_join=True,
                                 domain=[('booked', '=', False)])

    booked_line = fields.One2many('sale.order.line', 'order_id', string='Booked Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
                                 copy=True, auto_join=True,
                                 domain=[('booked', '=', True)])

    @api.model
    def is_booking(self):
        return len(self.booked_line) > 0

    @api.one
    def _compute_website_order_line(self):
        self.website_order_line = self.booked_line or self.order_line


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    booked = fields.Boolean(string='Prenotato', default=False)
