{
    'name': 'Booking',
    'category': 'Sales',
    'summary': 'Manage booking \'events\' for products',
    'version': '0.4',
    'description': """
Manage a booking section inside sales module
===================================================================

Features
--------
    * Create and manage booking events at the suppliers
    * Insert and manage a single booking from a customer for a given product in an event
    
    """,
    'author': 'Francesco Gabbrielli',
    'depends': ['product', 'purchase', 'sale'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/booking_model_acl.xml',
        'views/booking_views.xml'
    ]
}
