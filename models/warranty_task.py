from odoo import api, fields, models, _

class WarrantyTask(models.Model):
    _name = "inno.warranty.task"

    name = fields.Char(string = 'Task Description', help = 'Enter Tasks', required =True)




