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
        products = []
        for info in http.request.env['product.supplierinfo'].sudo().search([('name', '=', booking_event.supplier.id)]):
            products.append(info.product_tmpl_id)
        return http.request.render("website_booking.products", {
            'event': booking_event,
            'products': products
        })

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def book_cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        result = self.cart_update(product_id, add_qty, set_qty, **kw)
        if self.isBookingRoute:
            sale_order = http.request.website.sale_get_order()
            for line in sale_order.order_line:
                line.write({'booked': True})
        return result


    # @http.route(['''/book/<model("product.booking"):booking_event>/<model("product.template"):product>'''], type='http', auth='public', website=True)
    # def book_product_(self, booking_event, product, **kwargs):
    #     response = super().product(product, category=None, search='', **kwargs)
    #     response.qcontext['event'] = booking_event
    #     return response
    #     # return http.request.render("website_booking.product", {
    #     #     'event': booking_event,
    #     #     'product': product,
    #     #     'pricelist': http.request.website.get_current_pricelist()
    #     # })

    @http.route(['''/book/<model("product.booking.event"):booking_event>/<model("product.template"):product>'''],
                type='http', auth='public', website=True)
    def book_product(self, booking_event, product, **kwargs):
        return http.request.render("website_booking.product", {
            'event': booking_event,
            'product': product
        })

    def _get_search_domain(self, search, category, attrib_values):
        if self.isBookingRoute:
            #domain = http.request.website.sale_product_domain()
            #domain.remove(('sale_ok', '=', True))
            domain = [('id', 'in', search)]
            _logger.info("Products search domain %s: %s" % (domain, __name__))
            return domain
        return super()._get_search_domain(search, category, attrib_values)
