# Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io), certificate by [SignPath Foundation](https://signpath.org).

## Team roles

- **Committers and reviewers**: [duruoxian](https://github.com/duruoxian)
- **Approvers**: [duruoxian](https://github.com/duruoxian)

This is a single-maintainer project. The maintainer owns the source code repository, the build scripts, and the CI configuration.

## How releases are signed

All release binaries are built from this repository's source code by GitHub Actions
(see [`.github/workflows/build.yml`](.github/workflows/build.yml)) and submitted to
SignPath.io for signing. Every signing request is manually approved by the Approver.

Binaries are never built on a developer machine for release; only artifacts produced by
the documented CI workflow are signed, so that a signature confirms the binary is an
automated build of the source code in this repository.

## Privacy policy

See [PRIVACY.md](PRIVACY.md).
