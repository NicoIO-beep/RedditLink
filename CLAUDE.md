# CLAUDE.md — RedditLink

## Project Overview
<!-- Will be filled in after pitch -->

## Tech Stack
<!-- To be defined -->

## Project Structure
<!-- To be defined -->

---

## Development Guidelines

### General
- Keep it simple. No over-engineering, no speculative abstractions.
- Prefer editing existing files over creating new ones.
- No unnecessary comments, docstrings, or type annotations on untouched code.

### Code Style
- Follow the conventions already present in the codebase.
- Validate only at system boundaries (user input, external APIs). Trust internals.

### Git
- Commit early and often with clear, concise messages.
- Never force-push to main.
- Never commit secrets or .env files.

### Secrets & Environment
- All secrets live in `.env` (never committed).
- Use `.env.example` to document required variables without values.

### When in Doubt
- Ask before deleting or overwriting anything non-trivial.
- Measure twice, cut once.
