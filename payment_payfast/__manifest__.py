# -*- coding: utf-8 -*-
{
    'name': 'Payfast Payment',
    'category': 'ecommerce',
    'summary': 'Payment Acquirer: Payfast Implementation',
    'version': '0.1',
    'description': '''Make your transaction through Payfast''',
    'author': 'DRC Systems India Pvt. Ltd.',
    'website': 'www.drcsystems.com',
    'depends': ['payment'],
    'data': [
            'views/payment_views.xml',
            'views/payment_payfast_templates.xml',
            'views/account_config_settings_views.xml',
            'data/payment_acquirer_data.xml',
    ],
    'images': ['static/src/img/payfast.png'],
    'installable': True,
    'price': 40,
    'currency': 'EUR',
    'support':'support@drcsystems.com',
}
