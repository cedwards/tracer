Testing & Validation
====================

The following is a list of IP addresses currently running as Tracer nodes.
Note: These nodes are listed in the same order as listed in the current
``replication.map``.:

 * http://52.36.63.245/
 * http://52.27.135.176/
 * http://52.40.106.116/
 * http://52.40.253.162/
 * http://52.41.30.94/
 * http://52.38.241.159/

Accessible endpoints are: 
 * ``/docs/``
 * ``/cgit/``
 * ``/v1/list/<project>``
 * ``/v1/clone/<project>/<repo>``
 * ``/v1/fetch/<project>/<repo>``
 * ``/v1/list/<project>``

Test Cases
----------

 #. replicate a new repository (web / curl)
 #. update an existing repository (web / curl)
 #. view the documentation (web / curl)
 #. view the repositories (web / curl)
 #. validate replication (web / curl)
 #. validate cloning via http:// & git://
 #. list the repositories (web / curl)

Roadmap:
 #. read-write support (del repo, project, branch, tag, etc)

TODO:

 #. load testing
 #. hardware requirements
 #. apache config peer review
 #. tracer.wsgi peer review
 #. proposed system architecture
 #. github (enterprise) webhook configuration documentation (upstream?)
 #. github (enterprise) collaborators & teams documentation (upstream?)
