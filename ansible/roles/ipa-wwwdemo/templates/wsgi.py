#/usr/bin/python2
from pprint import pformat

HTML = """
<html>
<head>
    <title>{title}</title>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/example/css/patternfly.css"/>
</head>
<body>
<div class="container">
    <div class="page-header">
        <h1>{title}</h1>
    </div>
    <div class="container-fluid">
        <dl>
{envvars}
        </dl>
        <!--
        <pre>{env}</pre>
        -->
    </div>
</div>
</body>
</html>
"""


def application(environ, start_response):
    status = '200 OK'

    envvars = []
    prefixes = ('REMOTE_USER', 'REMOTE_GROUPS')

    # {% if app_mellon %}

    prefixes += ('MELLON_',)

    # {% endif %}

    for k, v in sorted(environ.iteritems()):
        if not k.startswith(prefixes):
            continue
        envvars.append('<dt>{0}</dt>'.format(k))
        if k.lower().endswith('groups'):
            envvars.append('<dd><ul>')
            for group in sorted(v.split(':')):
                envvars.append('    <li>{0}</li>'.format(group))
            envvars.append('</ul></dd>')
        else:
            envvars.append('<dd>{0}</dd>'.format(v))

    kwargs = dict(
        title='{{ app_title }}',
        envvars='\n'.join(envvars),
        env=pformat(environ)
    )
    output = HTML.format(**kwargs)

    response_headers = [
        ('Content-type', 'text/html'),
        ('Content-Length', str(len(output)))
    ]
    start_response(status, response_headers)
    return [output]
