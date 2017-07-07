#!/usr/bin/python2
import os
from pprint import pformat

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, 'ui', 'render.html')
LOGIN = os.path.join(HERE, 'ui', 'login.html')
ERROR = os.path.join(HERE, 'ui', 'error.html')

PREFIXES = ('REMOTE_USER', 'REMOTE_GROUPS', 'MELLON_')


def render(environ):
    kwargs = dict(
        title='Demo App',
        env=pformat(environ),
    )

    if environ.get('REMOTE_USER') is None:
        status = '401 Unauthorized'
        if (environ.get('REDIRECT_REMOTE_USER') is None and
                environ.get('SHOW_LOGIN')):
            template_file = LOGIN
        else:
            kwargs['strongmsg'] = environ.get('REDIRECT_EXTERNAL_AUTH_ERROR',
                                              'No REMOTE_USER')
            kwargs['msg'] = environ.get('REDIRECT_REMOTE_USER', '')
            template_file = ERROR
    else:
        status = '200 OK'
        template_file = CONTENT

        envvars = []
        for k, v in sorted(environ.iteritems()):
            if not k.startswith(PREFIXES):
                continue
            envvars.append('<dt>{0}</dt>'.format(k))
            if k.lower().endswith('groups'):
                envvars.append('<dd><ul>')
                for group in sorted(v.split(':')):
                    envvars.append('    <li>{0}</li>'.format(group))
                envvars.append('</ul></dd>')
            else:
                envvars.append('<dd>{0}</dd>'.format(v))

        kwargs['envvars'] = '\n'.join(envvars)

    with open(template_file) as f:
        template = f.read()
    output = template.format(**kwargs)
    return status, output


def application(environ, start_response):
    try:
        status, output = render(environ)
    except Exception as e:
        status = '500 Server Error'
        output = str(e)

    response_headers = [
        ('Content-type', 'text/html'),
        ('Content-Length', str(len(output)))
    ]
    start_response(status, response_headers)
    return [output]
