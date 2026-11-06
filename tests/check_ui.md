ui checks - automated app tests & browser verification

all tests run against app.py, not a mocked local replacement.
- six unanswered controls, generate disabled - pass
- case-a scores & plan, valid snapshot - pass
- case-b changes plan & practice topics - pass
- budget edit removes plan & download - pass
- answer edit removes plan & download - pass
- zero budget readable empty state - pass
- invalid course readable error - pass
- empty retrieval shortage messages - pass
- real browser profile download - pass, validated against the shared snapshot contract
- real browser budget edit clears old results - pass

browser was operated by codex, no human independent check claimed.
source download contained fictional case-a, no real student data.
