
from odoo import api, fields, models, _
from datetime import datetime,timedelta,time

class Service(models.Model):
    
    _name = "inno.service.details"
    _description = "Service Record"
    _inherit = ['mail.thread']
    _rec_name = 'warranty_id'

    @api.multi
    def count_task(self):
        count = self.env['project.task'].search_count([('project_id','=',"Service Task")])
        self.task_count = count

    name = fields.Char(string='Service ID',  copy=False,  index=True, default=lambda self: _('New'))
    warranty_id = fields.Many2one('inno.warranty.details',string='Warranty')
    product_id = fields.Many2one('product.product',string='Product', related='warranty_id.product_id')
    partner_id = fields.Many2one('res.partner',string='Customer', track_visibility='onchange', related='warranty_id.partner_id')
    # sno_id = fields.Many2one('inno.serial.number', string='Serial No', related='warranty_id.sno_id')
    warranty_end_date = fields.Date(string='Warranty End Date', related='warranty_id.warranty_end_date')
    date_received = fields.Date(string='Received Date',track_visibility='onchange',default=datetime.now())
    complaint_note = fields.Text(string='Description',track_visibility='onchange')
    service_note = fields.Text(string='Service Note')
    return_date = fields.Date(string='Date of Return',track_visibility='onchange')
    warranty_expired = fields.Boolean(string = "Warranty Expired", track_visibility='onchange')
    responsible_id = fields.Many2one(comodel_name="res.users", 
        string="Responsible", required=True,default=lambda self: self.env.user and self.env.user.id or False)
    task_count = fields.Integer(string='Task Count', compute = count_task)
    state = fields.Selection([('registered','Registered'),('approved','Approved'),
                              ('inservice','In Service'),
                              ('done','Service Done'),
                              ('delivered','Delivered'),
                              ('cancel', 'Cancelled'),], default='registered',string = "Status",track_visibility='onchange')
    @api.model
    def create(self,values):
        seq = self.env['ir.sequence'].get('inno.service.details') 
        values['name'] = seq
        result = super(Service,self).create(values)
        return result 

    @api.multi
    def action_state_process(self,vals):
        for service in self:
            service.state = 'inservice'

    @api.multi
    def action_state_approve(self,vals):
        for service in self:
            service.state = 'approved'
        
    @api.multi
    def action_state_done(self,vals):
        for service in self:
            service.state = 'done'
        
    @api.multi
    def action_state_deliver(self,vals):
        for service in self:
            service.state = 'delivered'
    
    @api.multi
    def action_state_cancel(self,vals):
        for service in self:
            service.warranty_expired = True
            service.state = 'cancel'
            
    @api.multi
    def action_warranty_task(self):
        task = self.env['project.task'].search([('project_id','=',"Service Task")])
        action = self.env.ref('project.action_view_task').read()[0]
        action['context'] = {'warranty_id':self.id}
        if len(task) > 1:
            action['domain'] = [('id', 'in', task.ids)]
        # elif len(task) == 1:
        #     action['views'] = [(self.env.ref('project.action_view_task').id, 'form')]
        #     action['res_id'] = task.ids[0] 
        else:
            action['domain'] = [('id', 'in', task.ids)]
        return action
    # vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:    
    
    # class ServiceTask(models.Model):
    #     _inherit = 'project.task'

    #     warranty_id = fields.Many2one(comodel_name='inno.warranty.details',string='Warranty')

    
    
    class ResPartner(models.Model):
        _inherit = 'res.partner'


    def send_msg(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_user_id': self.id},
                }