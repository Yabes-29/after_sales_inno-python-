

from odoo import api, fields, models, _
import datetime

class Warrantyextention(models.TransientModel):
    _name = "warranty.extention"
    _description = "Warranty Extention"
    
    extended_date = fields.Date(string='Warranty Extended Date')
    
    @api.multi
    def warrantyextended(self):
        active_warranty = self.env['inno.warranty.details'].browse(self._context.get('active_ids',[]))
        active_warranty.write({'warranty_end_date':self.extended_date,'state':'inwarranty'})
        active_warranty.message_post(body=_("Warranty Extended"))
        return True 

    

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2: