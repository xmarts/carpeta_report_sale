# -*- coding: utf-8 -*-pack
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    # App information 
    'name': "Product Profitability Report",
    'version': '12.0',
    'category': 'Sales',
    'summary' :'With Product Profitability Report app user can easily see the products profit in amount & percentage (%) for a specific time period.',
    'license': 'OPL-1',
    
    # Dependencies
    'depends': ['sale_stock','point_of_sale'],
    
    # Views
    'data': [
                'security/res_groups.xml',
                'security/ir.model.access.csv',
                'report/report_product_moves_ept_view.xml',
            ],
            
    # Odoo Store Specific
	'images': ['static/description/Product-Profitability-Report.jpg'],
	
	# Author 
    "author": "Emipro Technologies Pvt. Ltd.",
    'website': 'http://www.emiprotechnologies.com/',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',
               
    'installable': True,
    'auto_install': False,
    'application' : True,
    'live_test_url':'https://www.emiprotechnologies.com/free-trial?app=report-sale-profitability-ept&version=12&edition=enterprise',
    'price': '99',
    'currency': 'EUR',
}
