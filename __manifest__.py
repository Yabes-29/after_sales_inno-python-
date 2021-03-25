{
    'name': 'After Sales Innograph',
    'version': '0.1',
    'author' : 'Odoo Team PT. Innovasi Sarana Grafindo',
    'category': 'Sales',
    'license':'AGPL-3',
    'summary' : 'After Sales Innograph ',
    'description': """
The module helps to manage the warranty details and service information of products sold to customers and thus smoothen the after sales activities.
    """,
    'website': 'www.innograph.com',
    'depends': ['sale','account', 'base', 'product','mrp', 'mrp_production_draft', 'stock_mts_mto_rule', 'project', 'serial_pabrik'],
    'data': [
        'data/warranty_name_sequence.xml',
        'data/warranty_expire_scheduler.xml',
        'wizard/warranty_extention.xml',
        'views/warranty_record_view.xml',
        'views/service_record_view.xml',
        'views/campaign_record_view.xml',
        'views/product_template_view.xml',
        'views/warranty_task_analysis.xml',
        'views/warranty_task_view.xml',
        'views/sale_xpath.xml',
        # 'report/warranty_report.xml',
        # 'report/warranty_detail_report.xml',
        'report/warranty_card.xml',
        # 'wizard/whatsapp.xml',
        'wizard/wizard_whatsapp.xml',
        # 'views/sale_quotation.xml',
        # 'views/sale_task_analysis.xml',
        # 'views/sale_task_view.xml',
       
        #'security/ir.model.access.csv',
        #'views/security_group.xml'
        
    ],
    'images': ['static/description/inno_after_sales_banner.jpg'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:
