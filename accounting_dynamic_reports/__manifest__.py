# -*- coding: utf-8 -*-

{
    'name': 'Dynamic Financial Reports',
    'version': '10.0.1.0.2',
    'category': 'Accounting',
    'summary': "Balance Sheet & Profit and Loss Reports, Financial report, Dynamic Report, Odoo Accounting",
    'description': "This module creates dynamic Balance Sheet and P & L reports.",
    'author': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['account_accountant'],
    'data': [
        'views/templates.xml',
        'wizard/report_form.xml',
            ],
    'qweb': [
        'static/src/xml/report_tmpl.xml'],
    'license': 'OPL-1',
    'price': 19,
    'currency': 'EUR',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
