# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class Chapter(models.Model):
    _name = "chapter"
    _description = "Chapter"
    _order = "number, name"

    number = fields.Integer(index=True)
    name = fields.Char(index=True)
    story_id = fields.Many2one('story')
    version_ids = fields.One2many('chapter.version', 'chapter_id', copy=True)
    current_version_id = fields.Many2one('chapter.version')
    passage_ids = fields.One2many('passage', 'chapter_id', copy=True)
    summary = fields.Text()

    def open_record(self):
        view = {
            'name': _('Chapter'),
            'view_mode': 'form',
            'res_model': 'chapter',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': {'form_view_initial_mode': 'edit'},
        }
        return view


class ChapterVersion(models.Model):
    _name = "chapter.version"
    _description = "Chapter Version"
    _order = "version"

    chapter_id = fields.Many2one('chapter')
    version = fields.Integer(index=True)
    passage_ids = fields.One2many('passage', 'chapter_id', copy=True)
    summary = fields.Text()
