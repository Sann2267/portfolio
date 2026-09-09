## SOURCE CODE AVAILABILITY

A project may have an unavailable, deleted, private, or archived repository.

The application MUST NOT assume that every project has a public GitHub repository.

Repository fields are optional.

Allowed states:

- public
- private
- archived
- deleted
- unavailable

When the repository is unavailable:

- do not render a broken GitHub link
- do not fabricate a replacement repository
- do not claim that the source code is publicly accessible
- display available evidence instead
- allow the project to rely on documentation, screenshots, diagrams, demos, or technical descriptions

Example:

repository:
  status: unavailable
  url: null

UI:

SOURCE CODE
Unavailable

EVIDENCE
Documentation
Architecture
Screenshots
Technical Breakdown