from odoo import api, fields, models, _

class WarrantyTaskHistory(models.Model):
    _name = "inno.warranty.task.history"
    _rec_name = "warranty_id"

    warranty_id = fields.Many2one('inno.warranty.details', string='Order')
    warranty_task_id = fields.Many2one('inno.warranty.task', string='Pre-Delivery Task')
    done = fields.Boolean(string = 'Task Done', default = False)

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







