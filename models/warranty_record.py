from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Warranty(models.Model):
	
	_name = "inno.warranty.details"
	_inherit = ['mail.thread']
	_description = "Warranty Record"
	
	@api.multi
	def count_task(self):
		count = self.env['project.task'].search_count([('project_id','=',"Warranty Task")])
		self.task_count = count

	@api.multi
	def count_service(self):
		count = self.env['inno.service.details'].search_count([('warranty_id','=',self.id)])
		self.service_count = count
	
	@api.multi
	def count_campaign(self):
		count = self.env['inno.campaign.details'].search_count([('warranty_id','=',self.id)])
		self.campaign_count = count

	name = fields.Char(string='Warranty NO',  copy=False,  index=True, default=lambda self: _('New'))
	sale_id = fields.Many2one('sale.order', string='SO Reference')
	product_id = fields.Many2one('product.product', string="Product", related='sale_id.product_id' )
	partner_id = fields.Many2one('res.partner',string='Customer', related='sale_id.partner_id')
	bom_id = fields.Many2one('mrp.bom', string="Bill of Materials",)
	location_src_id = fields.Many2one('stock.location', string="Source Location", domain=[('usage', '=', 'internal')])
	location_dest_id = fields.Many2one('stock.location', string="Destination Location", domain=[('usage', '=', 'internal')])
	part_request_ids = fields.One2many('inno.part.request.line', 'part_request_id', string="Material Request Line")
	warehouse_id = fields.Many2one('stock.warehouse', string="User")
	picking_count = fields.Integer(compute="compute_picking_count")
	production_id = fields.Many2one('mrp.production', string="Production")
	manufacturing_id = fields.Many2one('mrp.production', string='MO Reference',)
	internal_reference = fields.Text(string='Internal Reference')
	sno_id = fields.Many2one('inno.serial.number', string='Serial No', )
	invoice_id = fields.Many2one('account.invoice',string='Invoice Reference')
	purchase_date = fields.Date(string='Delivery Date')
	warranty_end_date = fields.Date(string='Warranty End Date',track_visibility='onchange')
	qty_id = fields.Integer(string="Qty", required=True, default='1')
	state = fields.Selection([('inwarranty','In Warranty'),
							  ('toexpire','To Expire'),
							  ('expired','Expired')],string = "Status", default='inwarranty',track_visibility='onchange')
	not_interested = fields.Boolean(string="not interested",track_visibility='onchange')
	won_campaign = fields.Boolean(string = "won campaign",track_visibility='onchange')
	new_sales_id = fields.Many2one('sale.order',string='New sales reference')
	new_invoice_id = fields.Many2one('account.invoice',string='New invoice reference')
	service_count = fields.Integer(string='Service Count', compute = count_service)
	campaign_count = fields.Integer(string='Campaign Count', compute = count_campaign)
	task_count = fields.Integer(string='Campaign Count', compute = count_task)
	responsible_id = fields.Many2one(comodel_name="res.users", 
		string="Responsible", required=True, default=lambda self: self.env.user and self.env.user.id or False)
	# sparepart_ids = fields.One2many(comodel_name="inno.warranty.sparepart", 
	#     string="Component",
	#     inverse_name="warranty_id")
	pasang_id = fields.Char(string='Location',track_visibility='onchange')
	res_company = fields.Many2one('res.company',string='New sales reference')
	
	@api.multi
	def action_warranty_services(self):
		services = self.env['inno.service.details'].search([('warranty_id','=',self.id)])
		action = self.env.ref('inno_after_sales.sales_service_details_action').read()[0]
		action['context'] = {'default_warranty_id':self.id}
		if len(services) > 1:
			action['domain'] = [('id', 'in', services.ids)]
		elif len(services) == 1:
			action['views'] = [(self.env.ref('inno_after_sales.sales_service_details_form').id, 'form')]
			action['res_id'] = services.ids[0]  
		else:
			action['domain'] = [('id', 'in', services.ids)]
		return action
	
	@api.multi
	def action_warranty_campaign(self):
		campaign = self.env['inno.campaign.details'].search([('warranty_id','=',self.id)])
		action = self.env.ref('inno_after_sales.sales_campaign_details_action').read()[0]
		action['context'] = {'default_warranty_id':self.id}
		if len(campaign) > 1:
			action['domain'] = [('id', 'in', campaign.ids)]
		elif len(campaign) == 1:
			action['views'] = [(self.env.ref('inno_after_sales.sales_campaign_details_form').id, 'form')]
			action['res_id'] = campaign.ids[0] 
		else:
			action['domain'] = [('id', 'in', campaign.ids)]
		return action

	@api.model
	def cron_warranty_expire(self):
		date_eval =  datetime.now()+timedelta(days=30)
		date_eval_str = date_eval.strftime('%Y-%m-%d')
		warranty_records = self.env['inno.warranty.details'].search([('warranty_end_date','<=',date_eval_str),
																('state','=','inwarranty')])
		print '?????????warranty_records??????????',warranty_records
		for val in warranty_records:                        
			val.state = 'toexpire'
	 
	@api.model
	def cron_warranty_expired(self):
		date_eval =  datetime.now()
		date_eval_str = date_eval.strftime('%Y-%m-%d')
		warranty_records = self.env['inno.warranty.details'].search([('warranty_end_date','<=',date_eval_str)])
		print '==========warranty_records_expired==========', warranty_records
		for val in warranty_records:                        
			val.state = 'expired'        

	@api.model
	def default_get(self, fields):
		res = super(Warranty, self).default_get(fields)
		warehouse_obj = self.env['stock.warehouse']
		warehouse = warehouse_obj.search([('id', '=', 1)], limit=1)
		if warehouse:
			res['warehouse_id'] = warehouse.id
			res['location_src_id'] = warehouse.lot_stock_id.id
		return res
	
	@api.multi
	@api.onchange('production_id', 'production_id.partner_id', 
		'production_id.bom_id', 'production_id.product_id')
	def onchange_production_id(self):
		for doc in self:
			if doc.production_id:
				prod_id = doc.production_id
				doc.partner_id = prod_id.partner_id and prod_id.partner_id.id or False
				doc.bom_id = prod_id.bom_id.id
				doc.product_id = prod_id.product_id.product_tmpl_id.id
	
	@api.multi
	@api.onchange('product_id')
	def onchange_product_template(self):
		for doc in self:
			product = doc.product_id
			if product:
				bom_ids = product.bom_ids.filtered(lambda x: x.active == True)
				if any(bom_ids):
					doc.bom_id = bom_ids[0].id

	@api.multi
	@api.onchange('warehouse_id')
	def onchange_warehouse_id(self):
		for doc in self:
			wh = doc.warehouse_id
			if wh:
				doc.location_src_id = wh.lot_stock_id.id

	@api.multi
	def action_confirm(self):
		picking_type_obj = self.env['stock.picking.type']
		for req in self:
			src_loc = req.location_src_id
			dst_loc = req.location_dest_id
			domain = [('warehouse_id', '=', req.warehouse_id.id), 
						('code', '=', 'internal')]
			picking_type = picking_type_obj.search(domain, limit=1)
			values = {
				'location_id': src_loc.id,
				'location_dest_id': dst_loc.id,
				'min_date': req.date_scheduled,
				'origin': req.name,
				'picking_type_id': picking_type.id,
				'request_material_id': req.id
			}
			picking = self.env['stock.picking'].create(values)
			for line in req.part_request_ids:
				vals = {
					'product_id': line.product_id.id,
					'name': line.product_id.display_name,
					'product_uom_qty': line.quantity,
					'product_uom': line.uom_id.id,
					'location_id': src_loc.id,
					'location_dest_id': dst_loc.id,
				}
				move = self.env['stock.move'].create(vals)
				if move:
					picking.write({'move_lines': [(4, move.id)]})
					line.write({'move_id': move.id})
			picking.action_confirm()
			picking.action_assign()
		self.write({'state': 'confirm'})

	@api.multi
	def compute_picking_count(self):
		for req in self:
			moves = req.part_request_ids.mapped('move_id')
			picks = moves.mapped('picking_id')
			req.picking_count = len(picks)
	

	@api.multi
	def action_fill_part_request_lines(self):
		for req in self:
			part_line_obj = self.env['inno.part.request.line']
			moves_todo = self.env['stock.move']
			new_line_ids = []
			if req.production_id:
				# if have MO
				moves = req.production_id.move_raw_ids
				moves_todo = moves.filtered(lambda x: x.state in ['draft', 'waiting', 'confirmed'])
				bom_lines = req.bom_id and req.bom_id.bom_line_ids or self.env['mrp.bom.line']
				for move in moves_todo:
					line = bom_lines.filtered(lambda l: l.product_id.id == move.product_id.id)
					qty = (move.product_uom_qty - move.reserved_availability)
					vals = {
						'product_id': move.product_id.id,
						'description': move.product_id.display_name,
						'uom_id': move.product_uom.id,
						'quantity': qty,
						'item_size': line and line.item_size or False,
						'item_qty': line and line.item_qty or 0
					}
					new_line = part_line_obj.create(vals)
					new_line_ids.append(new_line.id)
			elif not req.production_id and req.bom_id:
				# If don't MO but have Bill of Materials
				for line in req.bom_id.bom_line_ids:
					vals = {
						'product_id': line.product_id.id,
						'description': line.product_id.display_name,
						'uom_id': line.product_uom_id.id,
						'quantity': line.product_qty,
						'item_size': line.item_size,
						'item_qty': line.item_qty
					}
					new_line = part_line_obj.create(vals)
					new_line_ids.append(new_line.id)
			if new_line_ids:
				req.write({'part_request_ids': [(6, 0, new_line_ids)]}) 
		return True
		

	@api.model
	def create(self, vals):
		if vals.get('bom_id') or vals.get('production_id'):
			vals['name'] = self.env['ir.sequence'].get('inno.warranty.details') 
			res = super(Warranty,self).create(vals)
			res.action_fill_part_request_lines()
		else:
			vals['name'] = self.env['ir.sequence'].get('inno.warranty.details') 
			res = super(Warranty,self).create(vals)
		return res


	@api.multi
	def write(self, vals):
		res = super(Warranty, self).write(vals)
		if 'bom_id' in vals or 'production_id' in vals:
			self.action_fill_part_request_lines()
		return res

	@api.multi
	def action_view_picking(self):
		moves = self.mapped('part_request_ids').mapped('move_id')
		pickings = moves.mapped('picking_id')
		action = self.env.ref('stock.action_picking_tree_all').read()[0]
		if len(pickings) > 1:
			action['domain'] = [('id', 'in', pickings.ids)]
		elif len(pickings) == 1:
			action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
			action['res_id'] = pickings.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		action['context'] = self.env.context
		return action

	def get_line_per10(self):
		""" Limit line per Page on Report """
		res = []
		all_line = self.part_request_ids
		total_page = len(all_line) // 10
		if len(all_line) % 10 != 0:
			total_page += 1
		index_slice = 0
		res_append = res.append
		for x in range(total_page):
			res_append(all_line[index_slice:index_slice + 10])
			index_slice += 10
		return res

	def get_picking(self):
		""" Get Picking for Report """
		moves = self.part_request_ids.mapped('move_id')
		picking = moves.mapped('picking_id')
		if picking:
			return picking[0].name

	def get_department(self):
		""" Get Department for Report """
		if self.user_id:
			emp = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
			if emp and emp.department_id:
				return emp.department_id.name
	
	@api.multi
	def action_endcampaigns(self,vals):
		for campaign in self:
			campaign.not_interested = True

	@api.multi
	def action_woncampaigns(self,vals):
		for campaign in self:
			campaign.won_campaign = True

	@api.multi
	def action_warranty_task(self):
		task = self.env['project.task'].search([('project_id','=',"Warranty Task")])
		action = self.env.ref('project.action_view_task').read()[0]
		action['context'] = {'warranty_id':self.id}
		if len(task) > 1:
			action['domain'] = [('id', 'in', task.ids)]
		else:
			action['domain'] = [('id', 'in', task.ids)]
		return action

	@api.depends('warranty_task_id')
	def warranty_checklist_progress(self):
		for rec in self:
			total_len = self.env['inno.warranty.task'].search_count([])
			check_list_len = len(rec.warranty_task_id)
			if total_len != 0:
				rec.warranty_checklist_progress = (check_list_len*100) / total_len
	
	warranty_task_id = fields.Many2many('inno.warranty.task', string='Check List')
	warranty_checklist_progress = fields.Float(compute=warranty_checklist_progress, string='Progress', store=True, recompute=True,
                                      default=0.0)
	max_rate = fields.Integer(string='Maximum rate', default=100)
	image = fields.Binary('Image')
	
class MrpPartRequestLineWarranty(models.Model):
	_name = 'inno.part.request.line'

	part_request_id = fields.Many2one('inno.warranty.details', string="Material Request")
	sale_id = fields.Many2one('sale.order', string='SO Reference')	
	product_id = fields.Many2one('product.product', string="Product")
	description = fields.Char()
	# serial_number_ids = fields.Many2many('serial.number.pabrik',string='Serial Number Pabrik')
	serial_number_pabrik = fields.Many2one('serial.number.pabrik',string = 'Serial Number Pabrik',)
	quantity = fields.Float()
	uom_id = fields.Many2one('product.uom', string="Unit of Measure")
	item_size = fields.Char()
	item_qty = fields.Integer()
	move_id = fields.Many2one('stock.move', string="Stock Move")
	

	@api.multi
	@api.onchange('product_id')
	def onchange_product_id(self):
		for line in self:
			line.uom_id = line.product_id and line.product_id.uom_id.id or False
# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:        
