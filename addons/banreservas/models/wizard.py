from odoo import models, fields, api


class FormsWizard(models.TransientModel):
    _name = "form.wizard"
    _description = "Banreservas"
    date = fields.Date()

    def export_forms_excel(self):
        related_model = self.env['banreservas.forms'] 
        return related_model.export_forms_excel(self.date)