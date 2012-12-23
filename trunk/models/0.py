from gluon.custom_import import track_changes; track_changes(True)

from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'Family Tree Publisher'
settings.subtitle = 'Publishing application for Agelong Tree'
settings.author = 'Andy Salnikov'
settings.author_email = 'famtreepub@salnikov.us'
settings.keywords = 'genealogy'
settings.description = 'This web application publishes genealogical information in the form of book pages or HTML page.'
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = 'ef077a8a-727b-4bbc-8431-312278cc8936'
settings.email_server = 'localhost'
settings.email_sender = 'a_salnikov@yahoo.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
