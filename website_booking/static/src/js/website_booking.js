odoo.define('website_booking.booking', function (require) {
"use strict";

var Class = require('web.Class');

var Booking = Class.extend({

    init: function() {
    },

    book: function(productId) {
        console.log(this._rpc({
            model: 'product.booking',
            method: 'book',
            args: productId
        }));
    }
});

var fieldRegistry = require('web.field_registry');
fieldRegistry.add('booking', Booking);

});