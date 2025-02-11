from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    campaign = fields.Char(string="Campaña")
    assigned_user_id = fields.Many2one('res.users', string='Vendedor asignado', help="Vendedor asignado al cliente")
    plan = fields.Char(string="Plan a ofrecer")
    start_date = fields.Datetime(string="Inicio")
    end_date = fields.Datetime(string="Vencimiento")
    equifax_type = fields.Selection([
        ('my_data', 'Mi data'),
        ('data', 'Data')
    ], string='Tipo de equifax')

