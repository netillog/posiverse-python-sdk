# OpenAPI recommended updates — 2026-09-29

Checked-in spec: `openapi/posiverse.openapi.json` (OpenAPI 3.0.1, info `v1.1.1`).
This file is a byte-for-byte copy of the owner attachment used for this sync.
SDK code on this branch follows that document. Removed helpers stay removed
(`get_logs`, `get_reports`, `get_device_data`, and related collectors).

## Live TEST run

Intended host: `https://openapi-test.posiverse.com` (shell `POSIVERSE_BASE_URL` only; not hardcoded in the library).
Production was not called.

`POSIVERSE_API_KEY` was not present in the cloud agent environment (process
environment, project `.env`, or any other local secret file). GitHub Actions
secret listing returned HTTP 403, so the key could not be read from the repo.
No key was invented and no authenticated request was sent.

Command (gate on, test base URL set, key absent):

```text
POSIVERSE_LIVE_INTEGRATION=1 POSIVERSE_BASE_URL=https://openapi-test.posiverse.com pytest -m live -q --tb=no
```

Result:

| Outcome | Count |
|---------|------:|
| passed | 0 |
| failed | 0 |
| skipped | 37 |

Every live test skipped in the `live_client` fixture because `POSIVERSE_API_KEY` is required. Skip is not a TEST response.

Mocked unit tests on the same revision: **92 passed**, 0 failed (`pytest -m "not live"`).

## Concrete mismatches

None. This run produced no response bodies, status codes, or field shapes from TEST, so there is no actual-vs-expected list to recommend.

`tests/integration/test_spec_probe.py` is ready to record wire kinds (device/user/settings-synched fields, device/telemetry/user log value kinds and timestamp scale, new vs old virtual-console paths, `tagId` list, and `GET /pages/{pageId}`) into `/tmp/posiverse-live-observations.json` on a future TEST run. Re-run that probe before treating any earlier 2026-09-24 notes as still true; those notes were not re-validated here.

## What still needs a TEST key

1. `GET /virtualconsole/{deviceId}/{lastDate}/{lastIdx}` with `lastDate=0` and `lastIdx=0` on the known fixture device (`016080001000367` / `9d9ba6c1-5ea5-d1b8-b78d-9b367a03f4c4`).
2. Whether `GET /virtualconsole/{deviceId}?lastDate=` still responds after the path move.
3. `GET /pages/{pageId}` when `x-next-page-url` is present.
4. Device-log behavior when both `imeis` and `deviceIds` are omitted, and when `startMillis` is omitted (spec: optional, server default 10 minutes ago, 365-day lookback, 30-day window).
5. Wire kinds for `DeviceLog.request` / `result` / `database`, `UserLog` the same, `TelemetryLog.json` and `date` / `serverDate` units, `User.language`, `SettingsSynched.ver` / `errors`, and `ConsoleLine.date`.
