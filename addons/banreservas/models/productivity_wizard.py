from odoo import fields, models, api

class ProductivityWizard(models.TransientModel):
    _name = 'productivity.wizard.banreservas'
    _description = 'Wizard para generar el reporte de productividad apartir de una fecha especifica'
    date = fields.Date(string='Fecha')

    def export_productivity_report(self):
        related_model = self.env['banreservas.forms']
        return related_model.export_form_productivity(self.date)

