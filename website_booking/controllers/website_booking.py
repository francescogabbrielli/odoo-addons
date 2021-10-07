import logging

from odoo import fields, http, tools
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)


class WebsiteBooking(WebsiteSale):
    """
    Odoo BUG: When inheriting controller, the super class is replaced up to first http.Controller subclass
    """

    # Fix Odoo BUG
    isBookingRoute = False

    # Fix Odoo BUG: re-exposing routes
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        self.isBookingRoute = False
        return super().shop(page=page, category=category, search=search, ppg=ppg, **post)

    @http.route(['/book'], type='http', auth='public', website=True)
    def book(self, page=0, category=None, search='', ppg=False, **post):
        events = http.request.env['product.booking.event']\
            .search([('status', '=', 'A')], order="date_from, title")
        return http.request.render("website_booking.events", {
            'events': events
        })

    @http.route(['''/book/<model("product.booking.event"):booking_event>'''],
                type='http', auth='public', website=True)
    def book_products(self, booking_event, **kwargs):
        self.isBookingRoute = True  # Fix Odoo BUG
        # allow products even if not published

        products = http.request.env['product.template']\
            .search([('id', 'in', booking_event.sudo().products.ids)])
        return http.request.render("website_booking.products", {
            'event': booking_event,
            'products': products
        })
        # return super().shop(page=0, category=booking_event.title, search=booking_event.sudo().products.ids, ppg=False, **kwargs)

    @http.route(['''/book/<model("product.booking.event"):booking_event>/<model("product.template"):product>'''],
                type='http', auth='public', website=True)
    def book_product(self, booking_event, product):
        return http.request.render("website_sale.product_item", {
            'product': product
        })

    def _get_search_domain(self, search, category, attrib_values):
        if self.isBookingRoute:
            domain = [('id', 'in', search)]
            _logger.info("Products search domain %s: %s" % (domain, __name__))
            return domain
        return super()._get_search_domain(search, category, attrib_values)
