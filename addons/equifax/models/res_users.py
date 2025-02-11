from odoo import models, fields, api

class ResUsers (models.Model):
    _inherit = 'res.users'

    is_agent = fields.Boolean(string='es agente?')