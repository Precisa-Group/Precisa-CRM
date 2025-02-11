from odoo import models, fields

class Address(models.Model):
    _name = 'res.address'
    _description = 'Direcciones'

    address = fields.Char('Direccion', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', ondelete='cascade')
    form_id = fields.Many2one('precisa_forms.form', string='Form', ondelete='cascade')

    def name_get(self):
        result = []
        for record in self:
            name = record.address or 'Sin direccion'
            result.append((record.id, name))
        return result
