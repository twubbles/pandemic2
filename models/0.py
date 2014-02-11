from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = 'testenv'
settings.subtitle = ''
settings.author = 'ejclairm'
settings.author_email = 'you@example.com'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'Default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = '91488f03-5d76-4e73-87ac-cc96b82d100e'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
