Tracer
======

This app replicates, updates and notifies peers regarding git webhook events.
GitHub Enterprise webhooks trigger the replication, and notify events are sent
to each node as defined in the ``replication.map``.

Defined endpoints are:
 * ``/docs/`` : usage instructions
 * ``/cgit/`` : web interface
 * ``/v1/clone/<project>/<repo>`` : clone / replicate repo
 * ``/v1/fetch/<project>/<repo>`` : fetch / update repo

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
        source: http://172.31.15.241

      172.31.17.241:
        notify:
          - 172.31.18.241
        source: http://172.31.16.241

      172.31.18.241:
        notify: False
        source: http://172.31.17.241

Roadmap
-------

 * ability to specify branch, tag, etc.
 * ability to delete branch, tag, etc.
