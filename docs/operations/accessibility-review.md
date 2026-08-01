# Accessibility review runbook

This runbook records the evidence required before closing CTW-090c. It supports a sole-developer
review and does not establish formal WCAG conformance.

## Automated browser evidence

Run the live Space with `playwright-cli` at the approved revision and record:

- first-tab skip-link reachability and activation;
- landmark, heading, table-header, link, and focus structure;
- 320px-wide reflow without horizontal overflow;
- simulated 200% zoom without horizontal overflow;
- content and aggregate-download availability after scripts are disabled or removed.

The receipt must include the URL, source/Space revisions, browser version, viewport sizes, date,
commands, results, and screenshots where useful.

## Human assistive-technology review

The recommended sole-developer path is NVDA on Windows:

1. Open the deployed Space with JavaScript enabled and disabled where the browser permits it.
2. Navigate by landmark, heading, and link using NVDA commands.
3. Confirm that the skip link, report table, provenance link, aggregate download, and boundary notice
   are announced meaningfully.
4. Repeat at 200% zoom and a narrow viewport.
5. Record defects, pass/fail status, browser/OS/NVDA versions, date, and reviewer identity.

If NVDA or another screen reader is unavailable, leave the human gate pending. Automated browser
evidence must not be relabelled as screen-reader evidence.

## Closure rule

Close issue #126 only when the automated receipt and human assistive-technology record are both
present. Record any remaining limitations explicitly and do not claim WCAG certification.
