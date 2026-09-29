# OpenAPI recommended updates — 2026-09-28 (live TEST)

Checked-in spec: `openapi/posiverse.openapi.json` (OpenAPI 3.0.1, info `v1.1.1`) on
branch `cursor/sync-openapi-sdk-02cd` (PR #15 head `92cda8da4631c29d25489c362e30a641c3cc8494`).
SDK on that revision follows the document. Removed helpers stay removed
(`get_logs`, `get_reports`, `get_device_data`, and related collectors).

This note **replaces** the placeholder in
`docs/notes/openapi-recommended-updates-2026-09-29.md` (which recorded an all-skip
run because the cloud agent had no `POSIVERSE_API_KEY`). Findings here come from a
real authenticated run against TEST on the box that holds the injected secret.
That placeholder file is removed; this path is the canonical note.

## Live TEST run

| Item | Value |
|------|-------|
| Host | `https://openapi-test.posiverse.com` via shell `POSIVERSE_BASE_URL` only |
| Production | Not called (`openapi-prod.posiverse.com` refused by live guard) |
| Gate | `POSIVERSE_LIVE_INTEGRATION=1` |
| Key | Present in box environment (never printed) |
| Fixtures | IMEI `016080001000367`, Device ID `9d9ba6c1-5ea5-d1b8-b78d-9b367a03f4c4` |
| When | 2026-09-28 ~17:27–17:29 PT |
| Working tree | `/workspace/posiverse-python-sdk-pr15` (GitHub archive of PR head) |

Command:

```text
POSIVERSE_LIVE_INTEGRATION=1 POSIVERSE_BASE_URL=https://openapi-test.posiverse.com pytest -m live -v --tb=short
```

Result (first run; second `-rs` confirmation matched):

| Outcome | Count |
|---------|------:|
| passed | 30 |
| failed | 0 |
| skipped | 7 |
| deselected (non-live) | 92 |

**Tests actually hit TEST** (not all-skip). The seven skips are intentional
“blocked” mutators (commands add / scratchpad delete / device update / groups
update / tenants update / users update / virtual-console send), not missing-key
skips.

Artifacts (non-secret):

- `docs/notes/posiverse-live-observations-2026-09-28.json` — from
  `tests/integration/test_spec_probe.py` (the live run wrote
  `/tmp/posiverse-live-observations.json`)
- The redacted pytest log stayed on the machine that ran TEST and is not in this repo.

## Wire kinds that match the checked-in spec

These actual shapes agree with the v1.1.1 document (no change recommended):

| Observation | Actual on TEST | Spec expectation |
|-------------|----------------|------------------|
| `GET /devices/{id}` VCM fields | `isVcmStatic` bool; `vcmProtocolId`, `vcmProtocolId2`, `vcmVehicleId` str | Same |
| `DeviceLog.database` | string UUID | `database` string (not `databaseId`) |
| `DeviceLog.result` | object | object |
| `DeviceLog.date` | int, millis-scale | int64 UTC millis |
| `DeviceLog.request` | absent on sampled row (optional) | optional object |
| `User.language` | string present | string |
| `SettingsSynched` | `ver` present; `errors` object; also `data`, `synchDate` | `ver` int64; `errors` object |
| `GET /virtualconsole/{deviceId}/{lastDate}/{lastIdx}` with `0/0` | **200**, empty list | Documented GET path |
| `GET /devicelogs` with `deviceIds` and **omitted** `startMillis` | **200** | `startMillis` optional (default ~10 min ago) |
| `GET /devices` (no tag) | **200**, 293 items, no `x-next-page-url` | OK |

Empty but successful samples (no item kinds to compare): telemetry logs (0),
user logs (0), new-path console lines (0).

## Concrete mismatches / recommendations

### 1. `GET /devices?tagId=` returns 400 SQL error (server bug)

- **Expected (spec):** `tagId` optional query on `GET /devices` — “Search for all
  devices associated with a specific tag using its UUID”.
- **Actual (TEST):** HTTP **400** with message
  `Unknown column 'tm.id' in 'on clause'`.
- **Recommend:** Fix TEST (and prod if same) join for tag→device listing, **or**
  temporarily mark `tagId` as broken / remove from the published OpenAPI until
  the column exists. SDK `client.devices.list(tag_id=…)` is correct per spec;
  the failure is backend.

### 2. `GET /devicelogs` without `imeis` and without `deviceIds` is 400

- **Expected (spec):** both `imeis` and `deviceIds` are `required: false`; text
  only says at most one of them may be provided.
- **Actual (TEST):** HTTP **400** —
  `deviceIds or imeis not provided`.
- **Recommend:** Document that **exactly one** of `imeis` or `deviceIds` is
  required (or make one of them `required: true` with a oneOf/XOR description).
  Current wording understates the live rule.

### 3. Old virtual-console GET still answers on TEST (undocumented)

- **Expected (spec):** reads live only on
  `GET /virtualconsole/{deviceId}/{lastDate}/{lastIdx}`. Path
  `/virtualconsole/{deviceId}` documents **PUT** only.
- **Actual (TEST):** `GET /virtualconsole/{deviceId}?lastDate=0` returned **200**
  with an empty list (compat behavior).
- **Recommend:** Either (a) keep documenting only the new path and treat old GET
  as unsupported/legacy (clients should migrate), or (b) re-document the old GET
  if it is intentionally retained. Do not rely on the old query form in the SDK
  (PR already uses the new path).

### 4. `GET /pages/{pageId}` not exercised this run

- Devices list returned the full page without `x-next-page-url` (293 items,
  `next: null`), so `client.pages.get` was not called against a real token.
- **Recommend:** No spec change from this run. Re-probe when a listing returns a
  next-page header (smaller `limit`, or a larger tenant dataset).

### 5. Telemetry / user-log / console line shapes not sampled

- Windows returned empty arrays for telemetry, user logs, and console output on
  the known fixture, so `TelemetryLog.json` / `date` / `serverDate` units and
  `ConsoleLine.date` / `UserLog.request|result|database` were **not** re-checked
  on the wire this time.
- Prior 2026-09-24 notes should not be treated as re-validated for those fields.
- **Recommend:** Optional follow-up with a wider time window or a device known to
  emit telemetry/console traffic; no new mismatch claimed here.

## What does **not** need a spec change from this run

- New virtual-console GET path works on TEST.
- Device VCM read field `vcmProtocolId2` (and write-side `vcmProtocol2Id` naming
  in `DevicePut`) matches the checked-in document for the fields we observed on
  read.
- `SettingsSynched.ver` / `errors`, `User.language`, `DeviceLog.database` rename
  and object `result` / millis `date` match live samples.
- Intentionally skipped mutators remain policy skips, not API failures.

## Suggested owner follow-ups (priority)

1. **P0:** Fix or document `GET /devices?tagId=` (SQL `tm.id` 400).
2. **P1:** Clarify OpenAPI that device-log queries require one of `imeis` /
   `deviceIds`.
3. **P2:** Decide fate of legacy `GET /virtualconsole/{deviceId}?lastDate=`.
4. **P3:** Re-run probe when pagination / telemetry / console samples exist.
