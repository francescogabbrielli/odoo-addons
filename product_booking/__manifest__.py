{
    'name': 'Prenotazioni',
    'category': 'Sales',
    'summary': 'Manage booking events for products',
    'version': '0.3',
    'description': 'Gestisce una sezione di prenotazioni all\'interno del modulo vendite',
    'author': 'Francesco Gabbrielli',
    'depends': ['product', 'purchase', 'sale'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/booking_model_acl.xml',
        'views/booking_views.xml'
    ]
}
