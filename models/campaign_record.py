from odoo import api, fields, models, _
from datetime import datetime,timedelta,time

class Campaign(models.Model):
    _name = "inno.campaign.details"
    _description = "Campaign Record"
    _inherit = ['mail.thread']
    _rec_name = 'warranty_id' 
    
    warranty_id = fields.Many2one('inno.warranty.details',string='Warranty')
    partner_id = fields.Many2one('res.partner',string='Customer',related='warranty_id.partner_id')
    capture_date = fields.Date(string='Capture Date',track_visibility='onchange')
    campaign_note = fields.Text(string='Note')
