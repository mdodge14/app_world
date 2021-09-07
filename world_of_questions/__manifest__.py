{
    'name': 'World of Questions',
    'version': '1.0.0.0.0',
    'author': "mdc",
    'website': '',
    'category': '',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'base',
    ],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/answer_views.xml',
        'views/challenge_views.xml',
        'views/question_views.xml',
        'views/solution_views.xml',
        'views/menu_views.xml',
        'wizard/get_solution_wizard_view.xml'
    ],
    'development_status': 'Production/Stable',
    # 'pre_init_hook': 'pre_init_hook',
    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
    # 'auto_install': False,
}
