# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _


class AddSolutionAnswerWizard(models.TransientModel):
    _name = 'add.solution.answer.wizard'
    _description = 'Add Solution Answer Wizard'

    for_solution = fields.Boolean()
    solution_id = fields.Many2one('solution')
    question_id = fields.Many2one('question')
    answer = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('sometimes', 'Sometimes'), ('kindof', 'Kind of')])

    def confirm(self):
        if self.solution_id.name and self.question_id.name and self.answer:
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

    def confirm_add(self):
        self.confirm()
        context = dict(
            self.env.context,
            default_solution_id=self.solution_id.id if self.for_solution else None,
            default_question_id=self.question_id.id if not self.for_solution else None,
            default_for_solution=self.for_solution
        )
        return {
            "name": "Add Answer",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "add.solution.answer.wizard",
            "target": "new",
            "binding_view_types": "form",
            "context": context,
        }
