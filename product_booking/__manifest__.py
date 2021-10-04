{
    'name': 'Prenotazioni',
    'category': 'Sales',
    'summary': 'Gestisce eventi di prenotazione prodotti presso fornitori',
    'version': '0.5',
    'description': """
Manage a booking section inside sales module
===================================================================

Features
--------
    * Create and manage booking events at the suppliers
    * Insert and manage a single booking from a customer for a given product in an event
    
    """,
    'author': 'Francesco Gabbrielli',
    'depends': ['product', 'purchase', 'sale', 'web_domain_field'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/booking_model_acl.xml',
        'views/booking_views.xml'
    ]
}
