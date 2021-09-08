# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)

class Challenge(models.Model):
    _name = "challenge"
    _description = "Challenge"
    # _order = "name"

    name = fields.Char(index=True)
    state = fields.Char(default="new")
    message = fields.Char(default="Would you like to play 20 questions?", readonly=True)
    question_id = fields.Many2one('question', string='Question')
    asked_question_ids = fields.Many2many('question', 'challenge_asked_questions', 'cid', 'qid')
    possible_solutions = fields.Many2many('solution', 'challenge_possible_solutions', 'cid', 'sid')
    question_is_possible_solution = fields.Boolean()
    answers = fields.Char()

    # TODO: Don't ask solution question if > 1 possible question to ask
    # TODO: When entering solution if article is 'a' or 'an' and solution changes, correct article to 'a'/'an'
    # TODO: Handle questions that might be answered wrong (e.g. flower in captivity)
    # TODO: Find/add data sources (e.g. reptile classifications, plant classifications, etc)
    def yes_action(self):
        if self.state in ('new', 'not playing', 'done'):
            self.message = "Great! I'll be the guesser. Do you know what you are?"
            self.state = 'ready'
        elif self.state == 'ready':
            self.ask_next_question()
        elif self.state == 'ask':
            return self.ask_next_question('yes')

    def no_action(self):
        if self.state in ('new', 'ready', 'done'):
            self.message = "OK, no problem. I'll be here when you're ready to play."
            self.state = 'not playing'
        elif self.state == 'ask':
            return self.ask_next_question('no')

    def kind_of_action(self):
        return self.ask_next_question()

    def not_sure_action(self):
        return self.ask_next_question()

    def start_over(self):
        self.state = 'new'
        self.name = "Hi there!"
        self.message = "Would you like to play 20 questions?"
        self.asked_question_ids = [(5, 0, 0)]
        self.possible_solutions = self.env['solution'].search([])
        self.question_is_possible_solution = False
        self.answers = None

    def eliminate_solutions(self, yes_or_no):
        remove = []
        for solution in self.possible_solutions:
            answer = self.env['answer'].search([('question_id', '=', self.question_id.id), ('solution_id', '=', solution.id)], limit=1)
            if answer.id and answer.answer != yes_or_no:
                remove.append(solution.id)
        for r in remove:
            self.possible_solutions = [(3, r, 0)]

    def get_remaining_questions(self):
        if self.asked_question_ids:
            questions = self.env['question'].search([('id', 'not in', self.asked_question_ids.ids)], order='sequence asc')
        else:
            questions = self.env['question'].search([], order='sequence asc')
        return questions

    def capture_answer(self, yes_or_no):
        answers = eval(self.answers) if self.answers else {}
        answers[self.question_id.id] = yes_or_no
        self.answers = str(answers)

    def check_out_of_questions(self):
        if self.asked_question_ids and len(self.asked_question_ids) >= 20:
            context = dict(
                self.env.context,
                default_challenge_id=self.id
            )
            return {
                "name": "I'm out of questions!",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "get.solution.wizard",
                "target": "new",
                "binding_model_id": "challenge",
                "binding_view_types": "form",
                "context": context,
            }
        return False

    def ask_next_question(self, yes_or_no=None):
        possible_solutions = []
        if yes_or_no:
            self.capture_answer(yes_or_no)
            self.eliminate_solutions(yes_or_no)
        out_of_questions = self.check_out_of_questions()
        if out_of_questions:
            return out_of_questions
        if yes_or_no:
            for solution in self.possible_solutions:
                answer = self.env['answer'].search([('question_id', '=', self.question_id.id), ('solution_id', '=', solution.id), ('answer', '=', yes_or_no)], limit=1)
                if answer.id:
                    possible_solutions.append(solution)
        if len(possible_solutions) == 0 and yes_or_no == 'no':
            answers = eval(self.answers) if self.answers else {}
            for solution in self.possible_solutions:
                add_solution = True
                for question_id in answers:
                    if answers[question_id] == 'yes':
                        answer = self.env['answer'].search([('question_id', '=', question_id), ('solution_id', '=', solution.id), ('answer', '=', 'yes')], limit=1)
                        if not answer.id:
                            add_solution = False
                            break
                if add_solution:
                    possible_solutions.append(solution)
        if len(possible_solutions) == 0:
            possible_solutions = self.possible_solutions
        if len(possible_solutions) == 1:
            answer = self.env['answer'].search([('solution_id', '=', possible_solutions[0].id), ('is_solution', '=', True)], limit=1)
            if answer.id:
                self.ask_question(answer.question_id)
                return
            else:
                possible_solutions = self.possible_solutions
        questions = self.get_remaining_questions()
        if len(questions) > 1:
            yes_answers = {}
            no_answers = {}
            for question in questions:
                for solution in possible_solutions:
                    answer = self.env['answer'].search([('question_id', '=', question.id), ('solution_id', '=', solution.id)], limit=1)
                    if answer.id:
                        if answer.answer == 'yes':
                            if question.id in yes_answers:
                                yes_answers[question.id] += 1
                            else:
                                yes_answers[question.id] = 1
                        elif answer.answer == 'no':
                            if question.id in no_answers:
                                no_answers[question.id] += 1
                            else:
                                no_answers[question.id] = 1

            best_question = questions[0]
            best_number_eliminated = 0
            if best_question.id in yes_answers and best_question.id in no_answers and yes_answers[best_question.id] >= no_answers[best_question.id]:
                best_number_eliminated = no_answers[best_question.id]
            elif best_question.id in yes_answers and best_question.id in no_answers and yes_answers[best_question.id] < no_answers[best_question.id]:
                best_number_eliminated = yes_answers[best_question.id]
            for question in questions:
                if question.id != best_question.id:
                    number_eliminated = 0
                    if question.id in yes_answers and question.id in no_answers and yes_answers[question.id] >= no_answers[question.id]:
                        number_eliminated = no_answers[question.id]
                    elif question.id in yes_answers and question.id in no_answers and yes_answers[question.id] < no_answers[question.id]:
                        number_eliminated = yes_answers[question.id]
                    if number_eliminated > best_number_eliminated:
                        best_question = question
                        best_number_eliminated = number_eliminated
        else:
            best_question = questions[0]
        self.ask_question(best_question)

    def ask_question(self, question):
        self.question_id = question.id
        self.asked_question_ids = [(4, self.question_id.id)]
        number = len(self.asked_question_ids) if self.asked_question_ids else 1
        self.name = "Question #{}".format(number)
        self.message = "{}?".format(self.question_id.name)
        self.state = 'ask'
        is_possible_solution = self.env['answer'].search([('question_id', '=', question.id), ('is_solution', '=', True)], limit=1)
        if is_possible_solution.id:
            self.question_is_possible_solution = True

    def solution_found(self):
        answers = eval(self.answers)
        answer = self.env['answer'].search([('question_id', '=', self.question_id.id), ('is_solution', '=', 'yes')], limit=1)
        solution = answer.solution_id
        for question_id in answers.keys():
            answer = self.env['answer'].search([('question_id', '=', question_id), ('solution_id', '=', solution.id)], limit=1)
            if not answer.id:
                self.env['answer'].create({
                    'solution_id': solution.id,
                    'question_id': question_id,
                    'answer': answers[question_id]
                })
        self.start_over()
        self.state = 'done'
        self.name = "I knew it!"
        self.message = "Would you like to play again?"
