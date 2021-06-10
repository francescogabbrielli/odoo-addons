# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from odoo import api, models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductBooking(models.Model):
    _name = 'product.booking'
    _description = 'Booking'
    _order = "code"

    code = fields.Char(string='Numero Prenotazione', readonly=True, default="/", size=6)

    title = fields.Char(string='Nome', required=True)
    description = fields.Text(string='Descrizione')

    date_from = fields.Date(string='Valida dal')
    date_to = fields.Date(string='Fino al')
    status = fields.Selection(string='Stato',
                              selection=[('A', 'Aperto'), ('C', 'Chiuso'), ('X', 'Annullato')])
    supplier = fields.Many2one('res.partner', string='Fornitore',
                               domain=[('supplier', '=', True)])
    products = fields.Many2many('product.supplierinfo', string='Prodotti prenotabili')
                                #domain=[('name', '=', supplier)]) non funziona

    @api.multi
    def name_get(self):
        return [(rec.id, "[%s] %s" % (rec.code, rec.title)) for rec in self]

    @api.model
    def create(self, vals):
        obj = super(ProductBooking, self).create(vals)
        if obj.code == '/':
            number = self.env['ir.sequence'].next_by_code('product.booking') or '/'
            obj.write({'code': number})
        return obj

    @api.onchange('supplier')
    def _onchange_supplier(self):
        _logger.info("On change supplier")
        if len(self.products) > 0:
            return {'value': {'products': [(5, 0, 0)]}}

    @api.one
    @api.constrains('products')
    def _check_products(self):
        if len(self.products) == 0:
            raise ValidationError("Non ci sono prodotti selezionati!")

    @api.one
    def book(self, product):
        return "Booked: %s!" % product


class ProductBookingLine(models.Model):
    _name = 'product.booking.line'
    _description = 'Booking Line'
    _order = 'product'
