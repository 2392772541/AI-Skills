---
name: readany
description: Use ReadAny CLI and MCP to safely access the user's local ReadAny library, notes, knowledge base, RAG context, and EPUB draft workflows.
---
<!-- readany-cli-managed -->

# ReadAny

Use this skill when the user asks an external AI agent to search, read, organize, or edit content stored in ReadAny.

## Capabilities

- Read book metadata, chapters, highlights, notes, bookmarks, and skills.
- Search ReadAny with metadata, keyword, semantic retrieval, and knowledge tools.
- Read the current reader context snapshot when the desktop client provides one.
- Inspect EPUB structure and use draft-first EPUB editing workflows when an editing profile is enabled.
- Read, patch, batch-patch, rebuild toc, inspect history, diff, undo, validate, discard, and export through ReadAny drafts.
- Export new artifacts only when the active profile allows export.
- Ask the user before high-risk actions.

## Safety Rules

- Start with readonly access unless the user explicitly asks for editing or publishing.
- Never request arbitrary shell, arbitrary SQL, or unrestricted filesystem access.
- Do not overwrite original books; use ReadAny drafts and exports.
- Treat publisher/export actions and draft discard as high-risk; ask the user to confirm in ReadAny.
- Prefer MCP tools in clients that support MCP. Use CLI commands as a transparent fallback.

## Client Setup Notes

- `all` setup links this managed skill into all known user skill discovery directories.
- `codex`, `claude`, `cursor`, and `opencode` setup link this managed skill into the known client skill directory.
- `agents` is a compatibility link under `~/.agents/skills/readany` for clients that follow OpenCode's agent-compatible lookup.
- `generic` setup only installs the CLI and canonical skill under `$AGENT_HOME/skills/readany`.

## MCP Tools

- `books.list` (low; scopes: book.read): List books in the ReadAny library.
- `books.search` (low; scopes: book.read): Search books by metadata and query text.
- `books.get` (low; scopes: book.read): Get metadata for a single book.
- `chapters.list` (low; scopes: content.read): List chapters for a ReadAny book from indexed chunks, or fallback EPUB/PDF structure when no chunks exist.
- `chapters.get` (low; scopes: content.read): Read a chapter from indexed chunks, or fallback EPUB/PDF content when no chunks exist.
- `context.get` (low; scopes: content.read): Read the latest desktop reader context snapshot, including current book, chapter, position, selection, surrounding text, and recent highlights when available.
- `bookmarks.list` (low; scopes: note.read): List bookmarks for a ReadAny book.
- `skills.list` (low; scopes: stats.read): List user-defined ReadAny AI skills and whether they are enabled.
- `notes.search` (low; scopes: note.read): Search notes in the ReadAny library.
- `notes.export` (high; scopes: epub.export): Export notes and highlights for one book to a markdown, JSON, Obsidian, or Notion file.
- `knowledge.export` (high; scopes: epub.export): Export the ReadAny library knowledge graph, including book metadata, notes, and highlights, to a file.
- `knowledge.search` (low; scopes: knowledge.read): Search ReadAny book metadata, notes, and highlights with bounded snippets and source references.
- `highlights.search` (low; scopes: note.read): Search highlights in the ReadAny library.
- `rag.search` (low; scopes: rag.search): Search indexed ReadAny book chunks using BM25 keyword retrieval.
- `audit.list` (low; scopes: stats.read): List recent ReadAny CLI/MCP audit entries without tool arguments or content payloads.
- `epub.inspect` (medium; scopes: epub.inspect): Inspect EPUB package metadata, manifest, spine, and table of contents.
- `epub.draft.create` (medium; scopes: epub.draft): Create a draft workspace for an EPUB without modifying the original book file.
- `epub.draft.discard` (medium; scopes: epub.draft): Discard an EPUB draft workspace and mark it as inactive.
- `epub.chapter.read` (medium; scopes: epub.draft): Read a chapter resource from an EPUB draft workspace.
- `epub.chapter.patch` (medium; scopes: epub.draft): Replace a readable XHTML chapter resource inside an EPUB draft workspace.
- `epub.chapters.patch` (high; scopes: epub.draft): Apply a bounded batch of chapter XHTML replacements to the same EPUB draft workspace.
- `epub.metadata.patch` (medium; scopes: epub.draft): Patch metadata fields inside an EPUB draft workspace package document.
- `epub.toc.rebuild` (medium; scopes: epub.draft): Rebuild the EPUB3 nav table of contents from draft spine chapters.
- `epub.history` (medium; scopes: epub.draft): Read operation history for an EPUB draft workspace.
- `epub.diff` (medium; scopes: epub.draft): Compare an EPUB draft workspace against its original source EPUB.
- `epub.undo` (medium; scopes: epub.draft): Undo one EPUB draft patch operation when no later edit changed the same resource.
- `epub.validate` (high; scopes: epub.export): Validate an active EPUB draft before export without modifying files.
- `epub.export` (high; scopes: epub.export): Export a validated EPUB draft to a new EPUB file.

## Commands

```bash
readany agent setup --user --client generic --profile readonly --json
readany agent setup --user --client codex --profile readonly --json
readany agent setup --user --client claude --profile readonly --json
readany agent setup --user --client cursor --profile readonly --json
readany agent setup --user --client opencode --profile readonly --json
readany agent setup --user --client all --profile readonly --json
readany doctor --json
readany mcp serve --profile readonly
readany mcp config --profile readonly --client generic --json
readany mcp config --profile readonly --client codex --json
readany mcp config --profile readonly --client claude --json
readany mcp config --profile readonly --client cursor --json
readany mcp config --profile readonly --client opencode --json
readany tools list --json
readany books list --json
readany books search <query> --json
readany book get <book-id> --json
readany chapters list <book-id> --json
readany chapter get <book-id> <chapter-id> --json --limit 12000
readany context get --json --limit 12000
readany bookmarks list <book-id> --json
readany skills list --json
readany notes search <query> --json --book <book-id>
readany highlights search <query> --json --book <book-id>
readany knowledge search <query> --json --book <book-id>
readany rag search <query> --book <book-id> --json
readany epub inspect <book-id> --profile editor --json
readany epub draft create <book-id> --profile editor --json
readany epub chapter read <draft-id> <chapter-id> --format xhtml --profile editor --json
readany epub chapter patch <draft-id> <chapter-id> --xhtml <file> --profile editor --json
readany epub chapters patch <draft-id> --patch <file> --profile editor --json
readany epub metadata patch <draft-id> --patch <file> --profile editor --json
readany epub toc rebuild <draft-id> --profile editor --json
readany epub history <draft-id> --profile editor --json
readany epub diff <draft-id> --profile editor --json
readany epub undo <draft-id> <operation-id> --profile editor --json
readany epub draft discard <draft-id> --profile editor --reason "finished" --json
readany epub validate <draft-id> --profile publisher --json
readany epub export <draft-id> --output <path> --profile publisher --json
readany notes export <book-id> --output <path> --profile publisher --json
readany knowledge export --output <path> --profile publisher --json
readany skill status --json
```

Managed by ReadAny CLI 0.1.0.
