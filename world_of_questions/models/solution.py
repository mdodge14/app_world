# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)

class Solution(models.Model):
    _name = "solution"
    _description = "Solution"
    # _order = "name"

    name = fields.Char(index=True)
    article = fields.Selection([('a', 'a'), ('an', 'an'), ('the', 'the')], default='a')
    questions_to_solution = fields.Integer(readonly=True)
    question_chain = fields.Text(readonly=True)
    solution_answers = fields.One2many('answer', 'solution_id', copy=True)
    yes_answers = fields.Text(readonly=True)

    def compute_yes_answers(self):
        for rec in self:
            rec.yes_answers = ""
            yes_answers = self.env['answer'].search([('solution_id', '=', rec.id), ('answer', '=', 'yes')])
            for answer in yes_answers:
                rec.yes_answers += "{}: {}\n".format(answer.question_id.name, answer.answer)

    def compute_question_chain(self):
        i = 1
        for rec in self:
            _logger.info("Computing question chain for {} of {}".format(i, len(self.ids)))
            rec.compute_solution_question_chain()
            i += 1

    def compute_solution_question_chain(self):
        _logger.info("Computing question chain for {}".format(self.name))
        solution_answer = self.env['answer'].search([('solution_id', '=', self.id), ('is_solution', '=', True)], limit=1)
        solution_question = solution_answer.question_id
        challenge = self.env['challenge'].create({'name': '{} compute question chain'.format(self.name)})
        challenge.start_over()
        challenge.yes_action()
        challenge.yes_action()
        self.question_chain = ""
        while challenge.question_id.id != solution_question.id and len(challenge.asked_question_ids) < 20:
            solution_answer = self.env['answer'].search([('solution_id', '=', self.id), ('question_id', '=', challenge.question_id.id)], limit=1)
            answer = solution_answer.answer if solution_answer.answer else 'Not Sure'
            self.question_chain += "{}: {}\n".format(challenge.question_id.name, answer)
            _logger.info("{} - {}: {}".format(self.name, challenge.question_id.name, answer))
            if answer == 'yes':
                challenge.yes_action()
            elif answer == 'no':
                challenge.no_action()
            elif answer == 'kindof':
                challenge.kind_of_action()
            elif answer == 'sometimes':
                challenge.sometimes_action()
            else:
                challenge.not_sure_action()
        self.questions_to_solution = len(challenge.asked_question_ids)
        challenge.unlink()

    def compute_solution_stripped(self, solution_name):
        solution_stripped = solution_name.title()
        if solution_stripped[0:2].lower() == 'a ':
            solution_stripped = solution_stripped[2:].lower()
        elif solution_stripped[0:3].lower() == 'an ':
            solution_stripped = solution_stripped[3:].lower()
        elif solution_stripped[0:4].lower() == 'the ':
            solution_stripped = solution_stripped[4:]
        return solution_stripped

    def compute_article(self, solution_stripped, article):
        if article == 'a' and solution_stripped[0].lower() in ('a', 'e', 'i', 'o', 'u'):
            article == 'an'
        elif article == 'an' and solution_stripped[0].lower() not in ('a', 'e', 'i', 'o', 'u'):
            article == 'a'
        return article

    def compute_solution_question(self, solution_stripped, article):
        return 'Are you {}{}'.format(article + ' ' if article else '', solution_stripped)

    @api.model
    def create(self, vals):
        res = super(Solution, self).create(vals)
        res.add_solution_answer()
        return res

    def add_answer(self):
        context = dict(
            self.env.context,
            default_solution_id=self.id,
            default_for_solution=True
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

    def add_solution_answer(self):
        solution_stripped = self.compute_solution_stripped(self.name)
        self.article = self.compute_article(solution_stripped, self.article)
        solution_question_text = self.compute_solution_question(solution_stripped, self.article)
        solution_question = self.env['question'].search([('name', 'ilike', solution_question_text)], limit=1)
        if not solution_question.id:
            solution_question = self.env['question'].create({'name': solution_question_text})
        answer = self.env['answer'].search([('question_id', '=', solution_question.id), ('solution_id', '=', self.id)], limit=1)
        if not answer.id:
            self.env['answer'].create({
                'solution_id': self.id,
                'question_id': solution_question.id,
                'answer': 'yes',
                'is_solution': True
            })

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(Solution, self).copy(default)
        solution_answer = self.env['answer'].search([('solution_id', '=', res.id), ('is_solution', '=', True)])
        solution_answer.unlink()
        answers = []
        remove_ids = []
        for answer in res.solution_answers:
            answer_str = "{}-{}".format(answer.solution_id.name, answer.question_id.name)
            if answer_str in answers:
                remove_ids.append(answer.id)
            else:
                answers.append(answer_str)
        remove_answers = self.env['answer'].search([('id', 'in', remove_ids)])
        remove_answers.unlink()
        return res
