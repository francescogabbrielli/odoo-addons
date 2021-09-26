# -*- coding: utf-8 -*-
import logging

from odoo import api, models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class BookingEvent(models.Model):
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


class Booking(models.Model):

    _name = 'product.booking'
    _description = 'Booking'
    _order = 'date,event,customer'

    name = fields.Char(string='Nome', readonly=True, compute='name_get')

    code = fields.Char(string='Numero Prenotazione', readonly=True, default="/", size=10)

    date = fields.Date(string='Data Prenotazione', default=fields.Date.today())
    customer = fields.Many2one('res.partner', string='Cliente', domain=[('customer', '=', True)])
    event = fields.Many2one('product.booking.event', string='Eventone')
    products = fields.Many2many('product.supplierinfo', string='Prodotti prenotati')

    @api.multi
    def name_get(self):
        return [(rec.id, "[%s] %s" % (rec.event.code, rec.code)) for rec in self]

    @api.model
    def create(self, vals):
        obj = super(Booking, self).create(vals)
        # _logger.info(self.event)
        if obj.code == '/':
            number = self.env['ir.sequence'].next_by_code('product.booking') or '/'
            obj.write({'code': number})
        return obj

    # TODO: onchange triggers even if the value does not really change...
    @api.onchange('event')
    def _onchange_event(self):
        # _logger.info("On change event %d" % len(self.event))
        return {
            'value': {'products': [(5, 0, 0)]},
            'domain': {'products': [('id', 'in', [p.id for p in self.event.products])]}
        }

    @api.one
    @api.constrains('products')
    def _check_products(self):
        if len(self.products) == 0:
            raise ValidationError("Non ci sono prodotti selezionati!")

    @api.depends('event')
    def _search_products(self):
        ret = [0]
        self.event.search()
        if self.event is not None:
            ret = [p.id for p in self.event[0][2].products]
        return [('id', 'in', ret)]


# -----------------------------------------------------------------------------
#
# FIXME: bug onchange
# ===================
#
# only way to set the domain on dependent field 'products' when editing existing
# 'booking' record, because onchange does not get called when opening the form
# (TODO: find a better solution...)
#

_domain = []


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        global _domain
        if len(domain) > 0 and domain[0] == "!" and len(fields) > 0 and fields[0] == "product_tmpl_id":
            domain = _domain + domain
        return super().search_read(domain, fields, offset, limit, order)


class BookingFix(models.Model):
    _inherit = "product.booking"

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        global _domain
        results = super().read(fields, load)
        if len(results) == 1 and 'products' in results[0]:
            _domain = [('id', 'in', [p.id for p in self.event.products])]
        return results
#
# -----------------------------------------------------------------------------
