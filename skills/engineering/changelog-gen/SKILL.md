---
name: changelog-gen
description: Generate a CHANGELOG section from conventional commits, deterministically, and decide the SemVer bump. Use when the user wants to update the changelog, cut release notes, draft a version, or summarize commits since a tag.
---

The changelog is generated, never hand-written. `skill-changelog` parses conventional-commit subjects into a Keep-a-Changelog section, grouped by type with breaking changes surfaced first, so the same history always renders the same notes. The tool takes the version as a literal label; choosing that version from the commits is the judgment this skill adds.

The grammar, the type-to-section map, the breaking-change rule, the SemVer decision, and the edge cases all live in [conventional commits](references/conventional-commits.md). Read that reference before deciding a version.

## Steps

1. **Pick the range.** Name the previous release tag as the start ref and the target ref (default `HEAD`) as the end. The range is exclusive at the start: `previous-tag..HEAD`. This step is done once both refs are named and the start tag resolves in the repo.

2. **Decide the version.** Read the commit subjects in the range, then climb the [SemVer ladder](references/conventional-commits.md) to the highest bump any single commit forces: a breaking `!` marker forces a major, a `feat` forces a minor, a `fix` forces a patch. This step is done once the new version string is written down with the one commit that justifies it.

3. **Generate the section.** Run `skill-changelog --version <version> --date <YYYY-MM-DD> --from <previous-tag> --to HEAD`. The output groups the parsed commits under fixed section titles, with breaking changes in their own block first; `--date` stamps the release date into the header, which the tool omits when the flag is absent. This step is done once a section prints with a `## [<version>] - <YYYY-MM-DD>` header.

4. **Review the groups.** Read the rendered section against the raw range to spot a commit that was dropped. A subject that landed in the wrong group, or vanished, points to a malformed or non-conventional commit subject rather than a tool defect. This step is done once every surviving commit sits under the section its type maps to.

5. **Write the file.** Rerun the same command — `skill-changelog --version <version> --date <YYYY-MM-DD> --from <previous-tag> --to HEAD --write CHANGELOG.md` — to prepend the section above the prior entries. The tool writes atomically and keeps the single top-level title, so the earlier history stays intact below the new block. This step is done once the command prints `wrote CHANGELOG.md`.

6. **Confirm the result.** Open `CHANGELOG.md` and read the top. This step is done once the new version sits at the top of the file with the prior history beneath it.

See also: [the determinism doctrine](../../meta/foundation/SKILL.md).

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
