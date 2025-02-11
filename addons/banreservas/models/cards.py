from odoo import models, fields, api


class banreservas_cards(models.Model):
    _name = "res.banreservas.cards"
    _description = "Tabla Límites x Ingresos"
    _rec_name = 'product'
    
    mark = fields.Char(string="Marca")
    minimum_income = fields.Char(string="Ingresos Mínimos")
    product = fields.Char(string="Producto")
    minimum_rd = fields.Char(string="Mínimo RD$")
    minimum_us = fields.Char(string="Mínimo US$")