# -*- coding: utf-8 -*-

from openerp import models, fields, api

class testaddon(models.Model):
    _name = 'testaddon.testaddon'

    name = fields.Char()
