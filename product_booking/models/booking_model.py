# -*- coding: utf-8 -*-
import logging

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import json

_logger = logging.getLogger(__name__)


class BookingEvent(models.Model):
    """
    An event where products can be booked at a supplier
    """
    _name = 'product.booking.event'
    _description = 'Booking Event'
    _order = "code"

    name = fields.Char(string='Nome', readonly=True, compute='name_get')

    code = fields.Char(string='Codice Evento', readonly=True, default="/", size=6)

    title = fields.Char(string='Titolo', required=True)
    description = fields.Text(string='Descrizione')
    date_from = fields.Date(string='Valida dal')
    date_to = fields.Date(string='Fino al')
    status = fields.Selection(string='Stato',
                              selection=[('A', 'Aperto'), ('C', 'Chiuso'), ('X', 'Annullato')])

    # only companies suppliers
    supplier = fields.Many2one('res.partner', string='Fornitore',
                               domain=[('supplier', '=', True), ('parent_id', '=', None)])
    # bookable products
    products = fields.Many2many('product.supplierinfo', string='Prodotti prenotabili')
    # -> NOTE: domain=[('name', '=', supplier)]) does not work, needs to be set on the view

    @api.multi
    def name_get(self):
        return [(rec.id, "[%s] %s" % (rec.code, rec.title)) for rec in self]

    @api.model
    def create(self, vals):
        obj = super(BookingEvent, self).create(vals)
        if obj.code == '/':
            number = self.env['ir.sequence'].next_by_code('product.booking.event') or '/'
            obj.write({'code': number})
        return obj

    @api.onchange('supplier')
    def _onchange_supplier(self):
        # _logger.info("On change supplier")
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


class Booking(models.Model):
    """
    A booking instance made by a customer, composed of one or more products chosen
    from a booking event
    """
    _name = 'product.booking'
    _description = 'Booking'
    _order = 'date,customer'

    name = fields.Char(string='Nome', readonly=True, compute='name_get')

    code = fields.Char(string='Numero Prenotazione', readonly=True, default="/", size=10)

    date = fields.Date(string='Data', default=fields.Date.today())

    customer = fields.Many2one('res.partner', string='Cliente', domain=[('customer', '=', True)])

    event = fields.Many2one('product.booking.event', 'Evento',
                                    index=True, ondelete='restrict', required=True)

    status = fields.Selection(string='Stato',
                              selection=[('A', 'Aperta'), ('C', 'Chiusa'), ('X', 'Annullata')],
                              default='A')

    products = fields.Many2many('product.template', string='Prodotti disponibili', compute="_compute_products", store=False)

    booking_lines = fields.One2many('product.booking.line', 'booking', string='Prodotti prenotati',
                                    help='Booking elements')

    total = fields.Float('Totale', default=0.0, compute="_compute_total")
    # event = fields.Many2one('product.booking.event', string='Evento')
    # products = fields.Many2many('product.supplierinfo', string='Prodotti prenotati')

    @api.multi
    def name_get(self):
        return [(rec.id, "[%s] %s" % (rec.event.code, rec.code)) for rec in self]

    @api.model
    def create(self, vals):
        # to enable @api.constrains
        if 'booking_lines' not in vals:
            vals['booking_lines'] = []

        obj = super(Booking, self).create(vals)

        # get sequence number
        if obj.code == '/':
            number = self.env['ir.sequence'].next_by_code('product.booking') or '/'
            obj.write({'code': number})

        return obj

    @api.constrains('booking_lines')
    def _check_products(self):
        if len(self.booking_lines) == 0:
            raise ValidationError("Non ci sono prodotti selezionati!")

    @api.depends('booking_lines')
    @api.onchange('event')
    def _onchange_event(self):
        global _selectedProducts
        _selectedProducts.clear()
        return {'value': {
            'booking_lines': [(5, 0, 0)]
        }}

    @api.multi
    @api.depends('event')
    def _compute_products(self):
        for rec in self:
            rec.products = [(6, 0, [p.product_tmpl_id.id for p in self.event.products])]

    @api.multi
    @api.depends('booking_lines')
    def _compute_total(self):
        global _selectedProducts
        _selectedProducts.clear()
        for rec in self:
            rec.total = 0
            for line in rec.booking_lines:
                _selectedProducts.append(line.product.id)
                rec.total += line.price * line.quantity

    @api.onchange('booking_lines')
    def _onchange_lines(self):
        global _selectedProducts
        _selectedProducts = [line.product.id for line in self.booking_lines]


# trick to store current selection in One2Many
_selectedProducts = []


class BookingLine(models.Model):
    """
    Relational Model: each product booked in an event, with its quantity specified
    """
    _name = 'product.booking.line'
    _description = 'Booking Line'

    booking = fields.Many2one('product.booking', 'Prenotazione', index=True, ondelete='cascade')

    event = fields.Many2one('product.booking.event', 'Evento', compute='_compute_event', store=False)

    product_domain = fields.Char(compute='_compute_product_domain', readonly=True)

    product = fields.Many2one('product.template', 'Prodotto',
                              index=True, ondelete='cascade', required=True,
                              domain='product_domain',
                              help="The product booked in the event")

    price = fields.Float('Prezzo', default=0.0, compute='_compute_price', readonly=True)

    quantity = fields.Integer('Quantità', default=1, required=True)

    def _compute_event(self):
        event_id = self.env.context['default_event_id']
        return self.env['product.booking.event'].search([('id', '=', event_id)])

    @api.multi
    @api.depends("product")
    def _compute_price(self):
        for record in self:
            try:
                info = record.product._get_combination_info()
                record.price = info['price']
            except Exception:
                pass

    @api.multi
    @api.depends('event')
    def _compute_product_domain(self):
        event = self._compute_event()
        for rec in self:
            rec.product_domain = json.dumps(
                [('id', 'in', [p.product_tmpl_id.id for p in event.products if p.product_tmpl_id.id not in _selectedProducts])]
            )



# -----------------------------------------------------------------------------
#
# FIXME: bug onchange
# ===================
#
# only way to set the domain on dependent field 'products' when editing existing
# 'booking' record, because onchange does not get called when opening the form
# (TODO: find a better solution...)
#
# _domain = []
#
#
# class SupplierInfoFix(models.Model):
#     _inherit = "product.supplierinfo"
#
#     # price = fields.Float('Prezzo', default=0.0, compute='_get_sale_price', readonly=True)
#
#     # @api.depends('product_tmpl_id')
#     # def _get_sale_price(self):
#     #     for record in self:
#     #         try:
#     #             info = record.product_tmpl_id._get_combination_info()
#     #             record.price = info['price']
#     #         except Exception:
#     #             pass
#
#     @api.model
#     def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
#         global _domain
#         if len(domain) > 0 and domain[0] == "!" and len(fields) > 0 and fields[0] == "product_tmpl_id":
#             domain = _domain + domain
#         return super().search_read(domain, fields, offset, limit, order)
#
#
# class BookingFix(models.Model):
#     _inherit = "product.booking"
#
#     @api.multi
#     def read(self, fields=None, load='_classic_read'):
#         global _domain
#         results = super().read(fields, load)
#         if len(results) == 1 and 'products' in results[0]:
#             _domain = [('id', 'in', [p.id for p in self.event.products])]
#         return results
# #
# # -----------------------------------------------------------------------------
