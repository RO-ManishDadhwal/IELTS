# Power Automate Flow Design (Production-Ready)

## Flow Name
`Teams-MoM-AutoGenerate-And-Distribute`

## Trigger strategy
**Type**: Recurrence (every 15 minutes, configurable).

Reason: robust fallback where a direct and reliable event for "recording stopped + transcript available" is unavailable.

---

## High-level steps

1. **Trigger: Recurrence**
2. **Initialize variables**
   - `varNowUtc`
   - `varLookbackStartUtc`
   - `varRunId`
3. **Get candidate meetings** (Graph API)
   - ended between lookback and now
4. **Apply to each meeting**
   1. Check dedup in audit list by `MeetingId`
   2. If already processed → skip
   3. Get meeting transcript metadata
   4. If transcript unavailable/empty → log waiting and continue
   5. Build attendee list (required + optional)
   6. Build transcript text payload
   7. Generate MoM using AI action with strict prompt
   8. Validate MoM structure
   9. If review enabled → approval action
   10. Send Outlook email to attendees
   11. Write audit success
5. **Catch/Scope failure handling**
   - log detailed error with run id + meeting id

---

## Detailed action list

## Scope: `S01_GetMeetings`
- **Action**: HTTP (Graph) `GET /users/{organizerUPN}/calendarView?...`
- Filter by date range using lookback window.
- Optional: only online meetings with Teams metadata.

## Scope: `S02_ProcessMeeting` (inside Apply to each)

### 2.1 Dedup check
- SharePoint `Get items` where `MeetingId eq '{id}' and Status eq 'Sent'`
- If count > 0 → `Terminate (SkippedAlreadyProcessed)`

### 2.2 Transcript fetch
- Graph:
  - list transcripts for online meeting
  - fetch latest transcript content
- Validate non-empty text length > configured minimum.

### 2.3 Attendee extraction
- Combine required + optional attendees + organizer.
- Normalize emails lower-case.
- Deduplicate.
- Remove blocked domains if policy configured.

### 2.4 AI generation (MoM)
- Use prompt template from `docs/templates/mom_prompt.md`.
- Inject:
  - meeting title/date/organizer/attendees
  - transcript text
- Return markdown/plain text MoM.

### 2.5 MoM validation gate
- Verify required headings exist:
  - Meeting Title
  - Date/Time
  - Organizer
  - Attendees
  - Agenda
  - Key Discussion Points
  - Decisions Made
  - Action Items
  - Risks / Blockers
  - Next Steps
  - Next Meeting Date
  - Summary
- If validation fails:
  - write audit `ValidationFailed`
  - optionally send to reviewer mailbox
  - do not send attendee email

### 2.6 Optional approval
- `Start and wait for an approval`
- If reject:
  - log `Rejected`
  - notify organizer with feedback link

### 2.7 Email dispatch
- Outlook `Send an email (V2)`
- To: deduplicated attendee list
- Subject format from config
- Body template from `docs/templates/email_template.html`

### 2.8 Audit success
- SharePoint create/update item:
  - `MeetingId`
  - `RunId`
  - `Status=Sent`
  - `Recipients`
  - `ProcessedAtUtc`

---

## Error handling pattern

Use parallel scopes:
- `Scope_Main`
- `Scope_OnError` configured with "run after has failed/timed out"

`Scope_OnError` actions:
1. Compose error object from `result('Scope_Main')`.
2. Write audit row `Status=Failed` with message + action name.
3. Optional admin alert email.

No silent failures; every exception path writes auditable status.

---

## Retry policy

- Graph HTTP actions: exponential retry, count 4.
- Outlook send: exponential retry, count 3.
- Transcript wait behavior: do not loop forever in one run. If not ready, mark `WaitingTranscript` for next recurrence.

---

## Idempotency key

`MeetingId` + `TranscriptId (optional)`

If same meeting has new transcript revision and policy allows re-send, treat as new revision; otherwise only first successful send.

