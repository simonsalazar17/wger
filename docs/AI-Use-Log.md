# AI Use Log — Final Project Documentation

- Used Codex to inspect repository artifacts and organize evidence for the software architecture document.
- Used Codex to draft Markdown prose and Mermaid diagrams for the feature's use case, logical model, interactions, activity flow, and state changes.
- Used Codex to compare the written descriptions with implementation files, test files, and commit history; verified external references for the cardio request, contribution guidance, and GDPR text.
- A review caught a stale security statement: an older trust-boundary note still called the upstream image URL unvalidated even though a later commit added an origin check. I checked the implementation and commit, then updated the finding to state both the control and its limits. This is an example of why generated summaries must be checked against code and history.
- The assistant also confirmed that the checked-in SBOM is not by itself evidence of a specific vulnerable dependency; without the prior scanner output and opened advisory, I left the CVE, version range, and reachability claim out instead of guessing.
- The AI did not run or alter the feature during this documentation task; the reported test output comes from the implementation work recorded in the repository/session.
- I will review the draft against the source files and course requirements, restore the missing dependency-advisory evidence, and correct any claim I cannot independently corroborate before submission.
