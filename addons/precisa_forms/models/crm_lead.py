from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_document = fields.Char(related='partner_id.document', string='email', store=True)
    partner_names = fields.Char(related='partner_id.first_name', string='nombres', store=True)
    partner_first_lastname = fields.Char(related='partner_id.last_name', string='Primer apellido', store=True)
    partner_second_lastname = fields.Char(related='partner_id.second_lastname', string='Segundo apellido', store=True)
    partner_cellphone = fields.Char(related='partner_id.mobile', string='Celular', store=True)

    def write(self, vals):
        result = super(CrmLead, self).write(vals)
        
        # Detectar si se ha actualizado el campo 'stage_id'
        if 'stage_id' in vals:
            # Buscar el formulario relacionado (precisa.form) si existe
            precisa_form = self.env['precisa_forms.form'].search([('lead_id', '=', self.id)], limit=1)
            if precisa_form:
                # Sincronizar estados entre 'crm.lead' y 'precisa.forms'
                if vals['stage_id'] == self.env.ref('crm.stage_lead1').id:
                    precisa_form.state = 'new'
                elif vals['stage_id'] == self.env.ref('crm.stage_lead2').id:
                    precisa_form.state = 'win'
                elif vals['stage_id'] == self.env.ref('crm.stage_lead3').id:
                    precisa_form.state = 'lost'
                elif vals['stage_id'] == self.env.ref('crm.stage_lead4').id:
                    precisa_form.state = 'call_back'
                elif vals['stage_id'] == self.env.ref('crm.stage_lead5').id:
                    precisa_form.state = 'untraceable'
                elif vals['stage_id'] == self.env.ref('crm.stage_lead6').id:
                    precisa_form.state = 'not_answered'

        return result