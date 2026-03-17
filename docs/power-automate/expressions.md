# Power Automate Expressions

## Time window

```text
utcNow()
```

```text
addMinutes(utcNow(), mul(-1, int(variables('cfg_lookbackMinutes'))))
```

## Safe text checks

```text
greater(length(trim(outputs('Compose_TranscriptText'))), int(variables('cfg_minTranscriptChars')))
```

## Attendee normalization

Lowercase:
```text
toLower(item()?['emailAddress']?['address'])
```

Null-safe map fallback:
```text
coalesce(item()?['emailAddress']?['address'], '')
```

## Remove empties from array

```text
filter(variables('varAttendeesRaw'), not(equals(item(), '')))
```

## Deduplicate array using union trick

```text
union(variables('varAttendeesClean'), variables('varAttendeesClean'))
```

## Required heading validation (example for one heading)

```text
contains(outputs('Compose_MoMText'), '## Meeting Title')
```

Combine all checks via `and(...)`:

```text
and(
  contains(outputs('Compose_MoMText'), '## Meeting Title'),
  contains(outputs('Compose_MoMText'), '## Date/Time'),
  contains(outputs('Compose_MoMText'), '## Organizer'),
  contains(outputs('Compose_MoMText'), '## Attendees'),
  contains(outputs('Compose_MoMText'), '## Agenda'),
  contains(outputs('Compose_MoMText'), '## Key Discussion Points'),
  contains(outputs('Compose_MoMText'), '## Decisions Made'),
  contains(outputs('Compose_MoMText'), '## Action Items'),
  contains(outputs('Compose_MoMText'), '## Risks / Blockers'),
  contains(outputs('Compose_MoMText'), '## Next Steps'),
  contains(outputs('Compose_MoMText'), '## Next Meeting Date'),
  contains(outputs('Compose_MoMText'), '## Summary')
)
```

## Email recipients string

```text
join(variables('varAttendeesDeduped'), ';')
```

## Subject format

```text
replace(variables('cfg_emailSubjectTemplate'), '{MeetingTitle}', outputs('Compose_MeetingTitle'))
```

