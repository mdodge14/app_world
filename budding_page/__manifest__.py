{
    'name': 'The Budding Page',
    'version': '1.0.0.0.0',
    'author': "mdc",
    'website': '',
    'category': '',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'base',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/chapter_views.xml',
        'views/passage_views.xml',
        'views/story_views.xml',
        'views/menu_views.xml',
    ],
    'development_status': 'Production/Stable',
}
