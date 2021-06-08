{
    'name': 'Prenotazioni Prodotto',
    'category': 'Website',
    'summary': 'Permette agli utenti di prenotare prodotti online attraverso Eventi di Prenotazione',
    'version': '0.2',
    'description': 'Gestisce una sezione di prodotti prenotabili all\'interno del negozio',
    'author': 'Francesco Gabbrielli',
    'depends': ['product_booking'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/website_booking.xml',
        'views/assets.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}
