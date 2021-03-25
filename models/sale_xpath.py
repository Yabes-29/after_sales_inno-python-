from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
	
	_inherit = "sale.order"


	@api.multi
	def count_warranty(self):
		count = self.env['inno.warranty.details'].search_count([('sale_id','=',self.id)])
		self.warranty_count = count


	warranty_count = fields.Integer(string='warranty Count', compute = count_warranty)

	@api.multi
	def action_warranty_warranty(self):
		warranty = self.env['inno.warranty.details'].search([('sale_id','=',self.id)])
		action = self.env.ref('inno_after_sales.sales_warranty_details_action').read()[0]
		action['context'] = {'default_sale_id':self.id}
		if len(warranty) > 1:
			action['domain'] = [('id', 'in', warranty.ids)]
		elif len(warranty) == 1:
			action['views'] = [(self.env.ref('inno_after_sales.sales_warranty_details_form').id, 'form')]
			action['res_id'] = warranty.ids[0]  
		else:
			action['domain'] = [('id', 'in', warranty.ids)]
		return action