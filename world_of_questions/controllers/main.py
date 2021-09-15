# -*- coding: utf-8 -*-
import logging
from odoo.http import request
from odoo import http, _, SUPERUSER_ID
from odoo.addons.web.controllers.main import Home

_logger = logging.getLogger(__name__)


class AppWebsite(Home):

    @http.route('/<int:challenge_id>/<string:answer>', type='http', auth="public", website=True, sitemap=True)
    def index(self, challenge_id, answer=None):
        if challenge_id:
            challenge = request.env['challenge'].with_user(SUPERUSER_ID).search([('id', '=', challenge_id)], limit=1)
        if not challenge.id:
            challenge = request.env['challenge'].with_user(SUPERUSER_ID).create({'name': 'Hi there!'})
        if answer == 'yes':
            challenge.yes_action()
        elif answer == 'no':
            challenge.no_action()
        elif answer in ('sometimes', 'kindof'):
            challenge.ask_next_question(answer)
        elif answer == 'unknown':
            challenge.ask_next_question()
        elif answer == 'guessed':
            challenge.solution_found()
        elif answer == 'r':
            challenge.start_over()
        else:
            if challenge.is_out_of_questions:
                return http.request.render('world_of_questions.get_solution', {'challenge': challenge})
            return http.request.render('world_of_questions.game_play', {'challenge': challenge})
        return request.redirect("/{}/o".format(challenge_id))

    @http.route(['/solution'], type='http', auth="public", website=True, sitemap=False)
    def add_solution(self, **post):
        challenge = request.env['challenge'].with_user(SUPERUSER_ID).search([('id', '=', post.get('challenge_id'))], limit=1)
        if post.get('solution') and post.get('question'):
            get_solution_wizard = request.env['get.solution.wizard'].with_user(SUPERUSER_ID).create({
                'challenge_id': int(post.get('challenge_id')),
                'solution': post.get('solution'),
                'article': post.get('article_select'),
                'solution_new_question': post.get('question'),
                'solution_answer': 'no' if post.get('answer-radio') == 'answer_no' else 'yes'
            })
            if get_solution_wizard.confirm():
                get_answers_wizard = request.env['get.answers.wizard'].with_user(SUPERUSER_ID).create({
                    'challenge_id': challenge.id,
                    'solution_id': get_solution_wizard.solution_id.id,
                    'question_id': get_solution_wizard.question_id.id,
                })
                return http.request.render('world_of_questions.get_answers', {'get_answers_wizard': get_answers_wizard})
        else:
            challenge.start_over()
        return request.redirect("/{}/o".format(challenge.id))

    @http.route(['/answers'], type='http', auth="public", website=True, sitemap=False)
    def add_answers(self, **post):
        get_answers_wizard = request.env['get.answers.wizard'].with_user(SUPERUSER_ID).search([('id', '=', post.get('get_answers_wizard_id'))], limit=1)
        get_answers_wizard.answer1 = post.get('answer1_select').lower() if post.get('answer1_select') else None
        get_answers_wizard.answer2 = post.get('answer1_select').lower() if post.get('answer2_select') else None
        get_answers_wizard.answer3 = post.get('answer1_select').lower() if post.get('answer3_select') else None
        get_answers_wizard.answer4 = post.get('answer1_select').lower() if post.get('answer4_select') else None
        get_answers_wizard.answer5 = post.get('answer1_select').lower() if post.get('answer5_select') else None
        get_answers_wizard.confirm()
        return request.redirect("/{}/o".format(get_answers_wizard.challenge_id.id))


class AppWebsiteController(http.Controller):

    @http.route(['/'], type='http', auth="public", website=True, sitemap=False)
    def play(self):
        challenge = request.env['challenge'].with_user(SUPERUSER_ID).create({'name': 'Hi there!'})
        return http.request.render('world_of_questions.game_play', {'challenge': challenge})
