# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import odoo
from odoo.tools import config
from . import models

_logger = logging.getLogger(__name__)

def empty(self):
    self.a = ''

def on_load():
    _logger.info('Begin on_load')
    #Note: Odoo registry loading will not have been completed yet when this is called. ORM operations won't work.
    #Try overriding _register_hook method in a model instead if you need to use ORM operations
    _logger.info("config['limit_time_real'] = {}, config['limit_request'] = {}".format(config['limit_time_real'], config['limit_request']))
    config['limit_time_real'] = None
    config['limit_request'] = None
    _logger.info("Updated config['limit_time_real'] to {}, config['limit_request'] to {}".format(config['limit_time_real'], config['limit_request']))
    _logger.info('End on_load')    
on_load()

def pre_init_hook(cr):
    _logger.info('Begin pre_init_hook')
    
    _logger.info('End pre_init_hook')

def post_init_hook(cr, registry):
    _logger.info('Begin post_init_hook')

    _logger.info('End post_init_hook')

def uninstall_hook(cr, registry):
    _logger.info('Begin uninstall_hook')

    _logger.info('End uninstall_hook')

