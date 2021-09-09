# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _


class AddSolutionAnswerWizard(models.TransientModel):
    _name = 'add.solution.answer.wizard'
    _description = 'Add Solution Answer Wizard'

    solution_id = fields.Many2one('solution')
    question_id = fields.Many2one('question')
    answer = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('sometimes', 'Sometimes'), ('kindof', 'Kind of')])

    def confirm(self):
        if self.question_id.name and self.answer:
            answer = self.env['answer'].search([('question_id', '=', self.question_id.id), ('solution_id', '=', self.solution_id.id)], limit=1)
            if answer.id:
                answer.answer = self.answer
            else:
                self.env['answer'].create({
                    'solution_id': self.solution_id.id,
                    'question_id': self.question_id.id,
                    'answer': self.answer
                })
            return
