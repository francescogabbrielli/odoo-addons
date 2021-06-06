import logging

from odoo import fields, http, tools
from odoo.addons.website_sale.controllers.main import WebsiteSale

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
        events = http.request.env['product.booking']\
            .search([('status', '=', 'A')], order="date_from, title")
        return http.request.render("website_booking.events", {
            'events': events
        })

    @http.route(['/book/products'], type='http', auth='public', website=True)
    def book_products(self, page=0, category=None, search='', ppg=False, **post):
        self.isBookingRoute = True  # Fix Odoo BUG
        return super().shop(page=page, category=category, search=search, ppg=ppg, **post)

    def _get_search_domain(self, search, category, attrib_values):
        domain = super()._get_search_domain(search, category, attrib_values)
        _logger.info("Products search domain %s: %s" % (domain, __name__))
        if self.isBookingRoute:
            domain.remove(('sale_ok', '=', True))
        #     domain += [('book_ok', '=', True)]
        return domain
