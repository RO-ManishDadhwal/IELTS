# Microsoft 365 Teams Recording → AI Minutes of Meeting (MoM) → Outlook Distribution

This repository provides a **production-ready, maintainable, auditable** implementation blueprint for automatically generating and emailing Minutes of Meeting (MoM) from Microsoft Teams meeting transcripts.

The implementation is intentionally **Power Automate-first** and uses native Microsoft 365 services wherever possible.

---

## 1) What this solution does

When a Teams meeting recording/transcript becomes available:

1. Detect eligible completed meetings.
2. Retrieve transcript/recap content.
3. Extract attendee email recipients.
4. Generate business-ready MoM using AI prompt design compatible with Microsoft 365 Copilot / AI Builder style actions.
5. Send MoM by Outlook email to attendees.
6. Log run details and errors for auditability.

---

## 2) Architecture decision (native-first, realistic constraints)

### Preferred architecture
- **Orchestration**: Power Automate cloud flow.
- **Meeting metadata/transcript source**: Microsoft Graph via HTTP with Entra ID app registration (required for robust transcript access in many tenants).
- **MoM generation**: AI prompt step (Copilot Studio/Azure OpenAI/AI Builder equivalent depending tenant capability).
- **Distribution**: Office 365 Outlook connector.
- **Audit log**: SharePoint list or Dataverse table (SharePoint list documented here for simplicity).

### Important technical limitation (explicit)
A fully reliable native trigger equivalent to *"exactly when Teams recording stops and transcript is fully available"* is not consistently exposed as a single turnkey Power Automate trigger across all tenants/licensing combinations.

Therefore this repo implements the **closest feasible production pattern**:

- **Fully automated**: scheduled polling flow every N minutes that detects newly ended meetings and processes only those with available transcript.
- **Human-review required (optional)**: approval step before emailing MoM if compliance requires review.

See [docs/power-automate/flow-design.md](docs/power-automate/flow-design.md).

---

## 3) Fully automated vs human-review-required

### Fully automated path
1. Scheduled trigger runs.
2. Find meetings ended in lookback window.
3. Verify transcript is present and non-empty.
4. Generate MoM draft from transcript.
5. Send MoM email to attendees.
6. Mark meeting as processed (idempotency).

### Human-review-required path (recommended for high-stakes meetings)
1. Steps 1–4 same as above.
2. Send approval request to organizer/PMO.
3. On approve → send email.
4. On reject → log outcome and request edits.

---

## 4) Files in this repository

- `docs/power-automate/flow-design.md` – end-to-end flow actions, control logic, retries, and failure handling.
- `docs/power-automate/expressions.md` – reusable Power Automate expressions.
- `docs/templates/mom_prompt.md` – strict MoM AI prompt (no hallucinated owners/dates/decisions).
- `docs/templates/email_template.html` – professional Outlook email template.
- `config/flow-config.example.json` – central configuration points.
- `samples/transcript_sample.json` – sample transcript payload.
- `samples/mom_output_example.md` – sample generated MoM output.

---

## 5) Configuration points

Edit `config/flow-config.example.json` (copy to tenant-specific secure config):

- `trigger.pollIntervalMinutes`: polling interval.
- `trigger.lookbackMinutes`: meeting end-time lookback.
- `graph`: tenant/client IDs and endpoints.
- `transcript`: language rules and minimum content checks.
- `attendees`: recipient inclusion policy.
- `ai`: prompt/model and temperature defaults.
- `email`: sender profile and subject format.
- `review`: optional approval gate.
- `audit`: SharePoint logging list details.

---

## 6) Prerequisites and permissions

## Licenses/Services
- Microsoft Teams Business.
- Power Automate.
- Outlook (Microsoft 365).
- Microsoft 365 Copilot (or compatible AI action route available in tenant).

## Technical dependencies
- Entra ID App Registration for Graph calls (if transcript APIs are needed).
- Power Automate premium connector usage may apply if using HTTP action.

## Microsoft Graph permissions (typical; validate with security team)
- `OnlineMeetings.Read.All`
- `OnlineMeetingTranscript.Read.All`
- `User.Read.All`
- `Calendars.Read`

Use least privilege and admin consent per tenant policy.

---

## 7) Setup steps

1. Create Entra ID app registration and capture:
   - Tenant ID
   - Client ID
   - Client secret/certificate
2. Create SharePoint list for audit and dedup tracking:
   - Columns: `MeetingId`, `ProcessedAtUtc`, `Status`, `RunId`, `ErrorMessage`, `Recipients`, `Organizer`.
3. Build Power Automate flow using `docs/power-automate/flow-design.md`.
4. Paste expressions from `docs/power-automate/expressions.md`.
5. Add AI prompt from `docs/templates/mom_prompt.md`.
6. Add Outlook email body from `docs/templates/email_template.html`.
7. Test with sample transcript and controlled pilot meetings.
8. Enable approval gate if governance requires manual review.

---

## 8) Validation and error handling built into design

- **Idempotency**: skip meetings already processed (by meeting ID).
- **Transcript availability check**: retry/poll until timeout window.
- **Attendee sanitization**: remove null/external blocked recipients based on policy.
- **MoM schema check**: ensure mandatory sections exist before send.
- **Fallback behavior**:
  - If transcript missing → log `WaitingTranscript` and retry on next run.
  - If AI response malformed → send to review queue, do not email attendees.
  - If Outlook send fails → retry with exponential backoff, then log hard failure.

---

## 9) Testing / runbook

## Recommended test cases
1. Meeting with transcript available quickly.
2. Transcript delayed by >1 polling cycle.
3. Meeting without transcript.
4. Internal + external attendees.
5. AI output missing required sections.
6. Organizer approval reject path.

## Run verification checklist
- Trigger cadence and lookback windows configured.
- Meeting IDs dedup correctly.
- Recipients are actual attendees and deduplicated.
- MoM contains required section headings and action table format.
- Email subject/body format correct.
- Audit records written for success/failure.

---

## 10) Known limitations

1. Exact event *"recording stopped and transcript ready"* may require polling fallback depending tenant capabilities.
2. Transcript quality depends on Teams transcription accuracy.
3. AI-generated summaries still require policy review for legal/compliance-sensitive meetings.

---

## 11) Security and compliance notes

- Do not store client secrets in plain text inside flow steps; use environment variables/Key Vault where available.
- Consider Data Loss Prevention (DLP) policy implications for AI and email connectors.
- Log only necessary metadata; avoid persisting full transcript unless retention policy allows it.

---

## 12) Operational ownership

- **Platform owner**: Power Platform admin.
- **Business owner**: PMO / Operations.
- **Support**: Workflow failure queue monitored daily.

