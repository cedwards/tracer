#!/usr/bin/env python2
'''
Tracer
======

This app replicates, updates and notifies peers regarding git webhook events.
GitHub Enterprise webhooks trigger the replication, and notify events are sent
to each node as defined in the ``replication.map``.

Defined endpoints are:
 * /docs/ : usage instructions
 * /cgit/ : web interface
 * /v1/list/<project> : list existing repo(s)
 * /v1/clone/<project>/<repo> : clone / replicate repo
 * /v1/fetch/<project>/<repo> : fetch / update repo

Note: /clone/ and /fetch/ can be used interchangeably and will automatically
call the appropriate underlying function.

Replication Map
---------------

The ``replication.map`` defines both the upstream and downstream nodes for each
member of the cluster. You can think of this map as representing hops in
network segments within your network. This example map defines connectivity
between four network segments by four Tracer nodes, with each node notifying
the next and cloning from the previous.

In actuality you may only require 2-3 hops, recursing even deeper is certainly
possible.

.. code-block:: yaml

    repo_path: /srv/http/api/repositories

    map:
      172.31.15.241:
        notify:
          - 172.31.16.241
        source: https://github.com

      172.31.16.241:
        notify:
          - 172.31.17.241
        source: http://172.31.15.241/cgit

      172.31.17.241:
        notify:
          - 172.31.18.241
        source: http://172.31.16.241/cgit

      172.31.18.241:
        notify: False
        source: http://172.31.17.241/cgit

Roadmap
-------

 * ability to specify branch, tag, etc.
 * ability to delete branch, tag, etc.
'''

from bottle import route, default_app, redirect, error
from bottle import response
import logging
import socket
import os

from sh import ls
from sh import git
import requests
import yaml

application = default_app()

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger('tracer')

IP_ADDR = socket.gethostbyname(socket.gethostname())
GIT_REPLICATION_MAP = '/srv/http/tracer/replication.map'


def _config(key):
    try:
        with open(GIT_REPLICATION_MAP) as fh_:
            config = yaml.safe_load(fh_)
            return config.get(key)
    except IOError:
        LOG.debug('Unable to load replication.map')


def _clone(project, repo):
    '''
    Clone (replicate) a new repository
    '''
    path = _config('repo_path')
    maps = _config('map')
    try:
        source = maps[IP_ADDR]['source']
    except KeyError:
        source = _config('default_source')

    upstream = '{0}/{1}/{2}'.format(source, project, repo)
    clone_url = '{0}/cgit/{1}/{2}'.format(source, project, repo)
    clone_path = '{0}/{1}'.format(project, repo)

    if not os.path.exists(os.path.join(path, project, repo)):
        if requests.get(clone_url):
            return git.clone('--mirror', clone_url, clone_path, _err_to_out=True, _cwd=path)
        if requests.get(upstream):
            return git.clone('--mirror', upstream, clone_path, _err_to_out=True, _cwd=path)
        else:
            parent_url = '{0}/v1/clone/{1}/{2}'.format(source, project, repo)
            requests.get(parent_url)
            return _clone(project, repo)
    return _fetch(project, repo)


def _fetch(project, repo):
    '''
    Fetch (update) an existing repository
    '''
    path = _config('repo_path')

    if os.path.exists(os.path.join(path, project, repo)):
        os.chdir(os.path.join(path, project, repo))
        git.fetch(_err_to_out=True)
        redirect('/cgit/' + project + '/' + repo)
        return
    return _clone(project, repo)


def _notify(project, repo):
    '''
    Notify peer(s)
    '''
    maps = _config('map')
    if maps[IP_ADDR]['notify']:
        for server in maps[IP_ADDR]['notify']:
            url = 'http://{0}/v1/clone/{1}/{2}'.format(server, project, repo)
            requests.get(url)
    else:
        LOG.debug('Not notifying any peers')


@route('/clone/<project>/<repo>', method='GET')
def clone(project, repo):
    '''
    Clone the repo; notify peer(s)
    '''
    response.content_type='application/json'
    repo_path = '{0}/{1}'.format(project, repo)

    _clone(project, repo)
    _notify(project, repo)
    redirect('/cgit/{0}'.format(repo_path))


@route('/fetch/<project>/<repo>', method='GET')
def fetch(project, repo):
    '''
    Fetch updates; notify peer(s)
    '''
    response.content_type='application/json'
    repo_path = '{0}/{1}'.format(project, repo)

    _fetch(project, repo)
    _notify(project, repo)
    redirect('/cgit/{0}'.format(repo_path))


@route('/list/<project>', method='GET')
def list(project):
    '''
    List repositories
    '''
    response.content_type='application/json'
    path = _config('repo_path')
    if not os.path.exists(path + '/' + project):
        return 'Repository not replicated'
    return ls(path + '/' + project)


@route('/docs')
def docs():
    response.content_type='application/json'
    output = '''
Supported endpoints are:

/cgit/ : cgit web interface
/v1/clone/&ltproject&gt/&ltrepo&gt : clone (replicate) project/repo
/v1/fetch/&ltproject&gt/&ltrepo&gt : fetch (update) project/repo

'''
    return output


@error(404)
def error404():
    response.content_type='application/json'
    output = '''
Supported endpoints are:</br>

/cgit/ : cgit web interface </li>
/v1/clone/&ltproject&gt/&ltrepo&gt : clone (replicate) project/repo
/v1/fetch/&ltproject&gt/&ltrepo&gt : fetch (update) project/repo

'''
    return output
