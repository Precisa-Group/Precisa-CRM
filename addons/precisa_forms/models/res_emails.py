from odoo import models, fields, api

class Email(models.Model):
    _name = 'res.email'
    _description = 'Emails'

    email = fields.Char('Correo electronico', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', ondelete='cascade')
    form_id = fields.Many2one('precisa_forms.form', string='Form', ondelete='cascade')

    def name_get(self):
        result = []
        for record in self:
            name = record.email or 'Sin Correo'
            result.append((record.id, name))
        return result
    
    @api.model
    def create(self, vals):
        # Si el formulario contiene un form_id, intentamos extraer el contact_id relacionado
        form = self.env['precisa_forms.form'].browse(vals.get('form_id'))
        if form and form.contact_id:
            vals['partner_id'] = form.contact_id.id

        return super(Email, self).create(vals)
