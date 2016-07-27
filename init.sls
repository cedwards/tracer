install-epel-release:
  pkg.installed:
    - name: epel-release
    - refresh: True
    - order: first

remove-epel-release:
  pkg.removed:
    - name: epel-release
    - order: last

git-daemon:
  pkg.installed: []
  service.running:
    - enable: True
    - name: git.socket

mod_wsgi:
  pkg.installed

python-bottle:
  pkg.installed

cgit:
  pkg.installed

python-pip:
  pkg.installed

sh_git:
  pip.installed:
    - name: sh
    - require:
      - pkg: python-pip

httpd:
  pkg.installed: []
  service.running:
    - enable: True
    - reload: True
    - require:
      - pkg: httpd
      - pkg: mod_wsgi
      - pkg: python-bottle
      - pip: sh_git
    - watch:
      - file: /etc/httpd/conf/httpd.conf
      - file: /etc/httpd/conf.d/20-cgit.conf
      - file: /etc/httpd/conf.d/10-tracer.conf
      - file: /srv/http/tracer/v1/tracer.wsgi
      - file: /etc/httpd/conf.modules.d/10-wsgi.conf

/var/lib/git:
  file.symlink:
    - target: /srv/http/tracer/repositories
    - force: True
    - require:
      - pkg: git-daemon

/etc/httpd/conf.d/20-cgit.conf:
  file.managed:
    - source: salt://tracer/templates/20-cgit.conf
    - require:
      - pkg: cgit

/etc/httpd/conf/httpd.conf:
  file.managed:
    - source: salt://tracer/templates/httpd.conf
    - require:
      - pkg: httpd

/etc/httpd/conf.d/10-tracer.conf:
  file.managed:
    - source: salt://tracer/templates/10-tracer.conf
    - require:
      - pkg: httpd

/srv/http/tracer/v1/tracer.wsgi:
  file.managed:
    - makedirs: True
    - source: salt://tracer/scripts/tracer.wsgi

/etc/httpd/conf.modules.d/10-wsgi.conf:
  file.managed:
    - source: salt://tracer/templates/10-wsgi.conf
    - require:
      - pkg: httpd
      - pkg: mod_wsgi

/srv/http/tracer/repositories:
  file.directory:
    - makedirs: True
    - user: apache
    - group: apache
    - mode: 755

/etc/cgitrc:
  file.managed:
    - template: jinja
    - source: salt://tracer/templates/cgitrc
    - require:
      - pkg: cgit

/srv/http/tracer/replication.map:
  file.managed:
    - source: salt://tracer/replication.map
