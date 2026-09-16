"""Live integration tests against https://openapi-test.posiverse.com only.

These tests are gated by ``POSIVERSE_LIVE_INTEGRATION=1`` (or the legacy
``POSIVERSE_LIVE_SMOKE=1``) and the ``live`` pytest marker. Default CI
runs exclude them via ``addopts = -m 'not live'``.
"""
