response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
    (T('Home'), False, URL('index'), []),
    (T('Mail'), False, 'mailto:famtreepub@salnikov.us?subject=Family%20Tree%20Publisher%20question', []),
    (T("Languages"), False, None, [
        ("English", session.ui_lang == 'en-us', URL('language', vars=dict(lang='en-us'))),
        ("Russian", session.ui_lang == 'ru', URL('language', vars=dict(lang='ru'))),
        ]
     )
]
