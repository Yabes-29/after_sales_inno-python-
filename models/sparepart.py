from odoo import api, fields, models
from datetime import datetime,timedelta,time

class Sparepart(models.Model):
	_name = "inno.warranty.sparepart"

	name = fields.Char(string="Material", required=True, size=100)#mau dibuat otomasi seperti Sales Order
	warranty_id = fields.Many2one("inno.warranty.details", string="Warranty")
	pabrik_id = fields.Char(string="Serial Number Pabrik",)
	qty_id = fields.Integer(string="Qty", required=True, default='1')
	status_id = fields.Char(string="Status", required=True,)
	description = fields.Text("Description")
	purchase_date = fields.Date(string='Delivery Date')
	warranty_end_date = fields.Date(string='Warranty End Date')
	product_id = fields.Many2one('product.product', string='Component',)
	# order_id = fields.Many2one('sale.order', string='Order Reference', required=True, 
			# ondelete='cascade', index=True, copy=False)
    # sale_task_id = fields.Many2one('sale.task', string='Product Task')
    # done = fields.Boolean(string = 'Task Done', default = False)

	
