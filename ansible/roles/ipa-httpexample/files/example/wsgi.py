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
            <dt>REMOTE_USER</dt>
            <dd>{username}</dd>
            <dt>REMOTE_USER_FULLNAME</dt>
            <dd>{fullname}</dd>
            <dt>REMOTE_USER_SN</dt>
            <dd>{sn}</dd>
            <dt>REMOTE_USER_GIVENNAME</dt>
            <dd>{givenname}</dd>
            <dt>REMOTE_USER_UID</dt>
            <dd>{uid}</dd>
            <dt>REMOTE_USER_EMAIL</dt>
            <dd>{email}</dd>
            <dt>REMOTE_GROUPS</dt>
            <dd>{remote_groups}</dd>
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
    kwargs = dict(
        title='Example app',
        username=environ.get('REMOTE_USER', 'n/a'),
        fullname=environ.get('REMOTE_USER_FULLNAME', 'n/a'),
        sn=environ.get('REMOTE_USER_SN', 'n/a'),
        givenname=environ.get('REMOTE_USER_GIVENNAME', 'n/a'),
        uid=environ.get('REMOTE_USER_UID', 'n/a'),
        email=environ.get('REMOTE_USER_EMAIL', 'n/a'),
        remote_groups=environ.get('REMOTE_USER_GROUPS', 'n/a'),
        env=pformat(environ)
    )
    output = HTML.format(**kwargs)

    response_headers = [
        ('Content-type', 'text/html'),
        ('Content-Length', str(len(output)))
    ]
    start_response(status, response_headers)
    return [output]
