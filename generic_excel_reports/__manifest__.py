# -*- coding: utf-8 -*-
##############################################################################
#
#    
#    Copyright (C) 2015 BrowseInfo(<http://www.browseinfo.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Odoo Dynamic Export Excel Reports For all Application',
    'version': '10.0.2.3',
    'sequence': 4,
    'summary': 'Easy to Export Excel view for all applications i.e CRM,Sales,Purchase,Invoices,Payment,Picking,Customer,Product Etc..',
    'category': 'Extra Tools',
    "price": 39,
    "currency": 'EUR',
    'description': """
	BrowseInfo developed a new odoo/OpenERP module apps.
	This module use for 
	-Export data in Excel
	-Global data Export
	-Global Export data for any object.
	-Export Sales Order in Excel, Export Sales data in Excel , Export purchase order in Excel, Export Purchase data in Excel.
	-Export Stock in Excel, Export Product data in Excel, Export Invoice on Excel, Export Product in Excel
	-Dynamic export,export in excel, Excel lead, excel sales order, download sales data, download purchase data, download invoice data
 
   """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base'],
    'data': [	"security/ir.model.access.csv",
		"views/generic_excel_report_view.xml",
        "views/template_view.xml"
             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}
