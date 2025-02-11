from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char(string='Primer nombre')
    last_name = fields.Char(string='Apellido')
    second_lastname = fields.Char(string="Segundo apellido")
    document = fields.Char(string="Cédula de Identidad", size=11)
    passport_document = fields.Char(string="Número de Pasaporte", size=20)
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino')
    ], string="Sexo", default='male')
    birth_place = fields.Char(string="Lugar de Nacimiento")
    birth_date = fields.Date(string="Fecha de Nacimiento")
    email_ids = fields.One2many('res.email', 'partner_id', string='Emails')
    address_ids = fields.One2many('res.address', 'partner_id', string='Direcciones')
    age = fields.Integer(string="Edad")
    suggested_product = fields.Char(string="Producto sugerido", require=True)
    suggested_limit = fields.Char(string="Limite sugerido", require=True)
    campaign = fields.Char(string="Campaña")

