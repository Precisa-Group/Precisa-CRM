from odoo import models, fields, api


class banreservas_offices(models.Model):
    _name = 'res.banreservas.offices'
    _description = 'Officinas comerciales de Banreserva'
    

    code = fields.Integer(string="Codigo")
    regional = fields.Char(string="Regional")
    office_name = fields.Char(string="Nombre Oficina")
    address = fields.Char(string="Direccion")
    province = fields.Many2one('res.country.state', string="Provincia")
    office_type = fields.Char(string="Tipo")
    schedule_one = fields.Char(string="Horario de Lunes a Viernes")
    schedule_two = fields.Char(string="Horario Sabados")
    schedule_three = fields.Char(string="Horario Domingos y dias feriados")

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.code or ''} - {record.office_name or ''}"
            result.append((record.id, name))
        return result
    
    