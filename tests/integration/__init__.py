"""Live integration tests gated by env vars.

These tests are gated by ``POSIVERSE_LIVE_INTEGRATION=1`` (or the legacy
``POSIVERSE_LIVE_SMOKE=1``), require ``POSIVERSE_BASE_URL``, and refuse
the production OpenAPI host. Default CI runs exclude them via
``addopts = -m 'not live'``.
"""
