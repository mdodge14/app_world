# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _


class GetSolutionWizard(models.TransientModel):
    _name = 'get.solution.wizard'
    _description = 'Get Solution Wizard'

    challenge_id = fields.Many2one('challenge', string='Challenge')
    solution = fields.Char()
    solution_question = fields.Char()
    solution_answer = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Yes/No')

    def confirm(self):
        if self.solution:
            answers = eval(self.challenge_id.answers)
            solution = self.env['solution'].create({'name': self.solution})
            for question_id in answers.keys():
                self.env['answer'].create({
                    'solution_id': solution.id,
                    'question_id': question_id,
                    'answer': answers[question_id]
                })
            if self.solution_question and self.solution_answer:
                question = self.env['question'].create({'name': self.solution_question})
                self.env['answer'].create({
                    'solution_id': solution.id,
                    'question_id': question.id,
                    'answer': self.solution_answer
                })
            question = self.env['question'].create({'name': 'Are you a {}'.format(self.solution)})
            self.env['answer'].create({
                'solution_id': solution.id,
                'question_id': question.id,
                'answer': 'yes',
                'is_solution': True
            })
        self.challenge_id.start_over()
        return

    def skip(self):
        self.challenge_id.start_over()
        return