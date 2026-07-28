# Security scanning policy

The repository runs Bandit as a required local and hosted security gate.

The checked-in .bandit policy excludes only findings that are expected from
the harness architecture:

- B101: internal invariant assertions are used for typed model branches;
- B310: URL requests are made through bounded, validated source and metadata
  adapters rather than arbitrary user-provided URLs;
- B404, B603, and B607: subprocess calls use fixed argument lists for
- B104: the dashboard binds to all container interfaces because the hosted
  server must accept traffic from the container runtime.
  repository/tool inspection and do not invoke a shell.

Tests are scanned by the normal test and CodeQL workflows rather than this
runtime-tool scan. New suppressions require a code-reviewable policy change and
an explanation here.
