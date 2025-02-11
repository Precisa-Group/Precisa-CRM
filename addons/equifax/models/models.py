# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Equifax(models.Model):
    _name = 'equifax'
    _description = 'Equifax Record'

    name = fields.Char(string="Nombre", compute="_compute_data", store=True, readonly=True)
    partner_id = fields.Many2one(
        'res.partner', 
        string="Cliente", 
        
    )
    document = fields.Char(string="Cédula")
    campaign = fields.Char(related='partner_id.campaign', string="Campaña", store=True, readonly=True)
    user_id = fields.Many2one('res.users', string="Vendedor", store=True, readonly=True)
    plan = fields.Char(string="Plan", readonly=True)
    stage_id = fields.Many2one(
        'equifax.stage', 
        string="Estado",
        group_expand='_read_group_stage_ids', 
        tracking=True
    )
    gender = fields.Selection([
        ('Female','Femenino'),
        ('Male','Masculino')
    ], string="Genero", readonly=True)
    email = fields.Char(string="Correo", readonly=True)
    phone = fields.Char(string="Teléfono", readonly=True)
    telephone = fields.Char(string="Celular", readonly=True)
    start_date = fields.Datetime(string='Inicio', readonly=True)
    end_date = fields.Datetime(string='Vencimiento', readonly=True)
    contact_date = fields.Date(string="Fecha de contacto")
    comment = fields.Text(string="Comentario")


    # @api.onchange('partner_id')
    # def _check_document_unique(self):
    #     for record in self:
    #         if self.search_count([('document', '=', record.document)]) >= 1:
    #             raise ValidationError("Existe un formulario creado para este cliente")

    # @api.onchange('document')
    # def _check_document_unique(self):
    #     for record in self:
    #         if self.search_count([('document', '=', record.document)]) >= 1:
    #             raise ValidationError("Existe un registro creado para este cliente")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['equifax.stage'].search([])
    
    @api.depends('document', 'partner_id')
    def _compute_data(self):
        for record in self:
            if record.document:
                contact_id = self.env['res.partner'].search([('document', '=', record.document)], limit=1)
                if contact_id:
                    record.partner_id = contact_id
                    record.comment = record.comment if record.comment else  ''
                    record.update_from_partner(contact_id)
            elif record.partner_id:
                record.update_from_partner(record.partner_id)

    def update_from_partner(self, partner):
        self.name = partner.name
        self.document = partner.document
        self.phone = partner.phone
        self.telephone = partner.mobile
        self.gender = partner.gender
        self.plan = partner.plan
        self.user_id = partner.user_id
        self.email = partner.email
        self.start_date = partner.start_date
        self.end_date = partner.end_date
        

    @api.constrains('document')
    def _check_document_unique(self):
        for record in self:
            if self.search_count([('document', '=', record.document)]) >= 1:
                raise ValidationError("Existe un formulario creado para este cliente")

