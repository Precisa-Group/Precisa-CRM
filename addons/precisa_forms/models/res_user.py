from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    br_code = fields.Char(string="Codigo banreservas")

#     current_form = fields.Selection([
#         ('lafice', 'Lafice'),
#         ('banreservas', 'Banreservas')
#     ], string='Current Form', default=False)
