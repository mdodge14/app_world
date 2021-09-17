# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class Story(models.Model):
    _name = "story"
    _description = "Story"
    _order = "name"

    name = fields.Char(index=True)
    version_ids = fields.One2many('story.version', 'story_id', copy=True)
    current_version_id = fields.Many2one('story.version')
    chapter_ids = fields.One2many('chapter', 'story_id', copy=True)

    def open_record(self):
        view = {
            'name': _('Story'),
            'view_mode': 'form',
            'res_model': 'story',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': {'form_view_initial_mode': 'edit'},
        }
        return view


class StoryVersion(models.Model):
    _name = "story.version"
    _description = "Story Version"
    _order = "version"

    story_id = fields.Many2one('story')
    version = fields.Integer(index=True)
    chapter_ids = fields.One2many('chapter', 'story_id', copy=True)
