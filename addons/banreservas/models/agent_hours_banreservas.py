from odoo import models, fields


class AgentHoursBanreservas(models.Model):
    _name = 'agent.hours.banreservas' 

    date = fields.Date()
    hours = fields.Float(string="Hours", digits=(12, 2))
   