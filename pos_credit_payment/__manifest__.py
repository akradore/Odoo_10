# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    "name" : "POS Customer Credit Payment Odoo/OpenERP",
    "version" : "10.0.0.2",
    "category" : "Point of Sale",
    "depends" : ['base','sale','sales_team','point_of_sale'],
    "author": "BrowseInfo",
    "price": 129.00,
    "currency": 'EUR',
    'summary': 'Allow Credit Payment Feature for Customer which uses on POS and adjust POS payment with allow credit from Customer',
    "description": """
    BrowseInfo developed a new odoo/OpenERP module apps.
    Purpose :- 
Purpose of this feature is, We have define credit to selected customer, so customer's can purchases any items according to their credit availability.


Features:-

 We have created Credit Details menu in Sales. From that we can add credit for customer.
 We have created smart button on customer form view which shows how much credit available for that customer.
 We made a credit journal in accounting for payment. Which is also show in POS configuration payment options.
 POS credit Payment, POS Debit Payment, Customer Credit on POS, POS payment with credit payment, Customer POS credit payment, POS customer Payment, Customer Credit Payment on POS, POS Credit feature, Allow Credit on POS,Point of sale credit payment, POS partial payment, POS partial credit payment, POS credit with customer, Point of sale customer credit payment.
Point of sale credit Payment, Point of sale Debit Payment, Customer Credit on point of sale, point of sale payment with credit payment, Customer point of sale credit payment, point of sale customer Payment, Customer Credit Payment on point of sale, point of sale Credit feature, Allow Credit on point of sale, point of sale partial payment, point of sale partial credit payment, point of sale credit with customer.


So Now In POS..

 Validations:-
- Can not use credit payment option if there is no customer selected. It will be raise Error popup.
- if product is not selected then It will be raise Error popup in POS.
- Customer should not pay more than its credit availablity and not more than order amount.
- Customer can use lesser amount from his credit for total order amount. And for remaining amount he/she can use another journal(payment option).
- When customer has used its credit for purchasing item than it will be automatically deducted from his credit and it will be also affected at backend of Odoo.
    Module has following features.
    -Point of sale credit payment, customer credit on POS, Point of sale Customer Credit,Cash Counter credit, Payment Credit
    -POS credit payment, Point of Sale credit payment, Credit payment on POS, POS partial payment, POS partial credit payment. POS customer partial payment.
    """,
    "website" : "www.browseinfo.in",
    "data": [
        'security/ir.model.access.csv',
        'views/custom_sale_view.xml',
        'views/custom_pos_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos_extended.xml',
    ],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
