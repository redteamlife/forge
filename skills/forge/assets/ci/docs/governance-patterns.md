# FORGE Governance Storage

FORGE governance documents in `docs/forge/` can be managed in three patterns.

## Embedded

`docs/forge/` is committed alongside code.

Use when governance artifacts may live in the project repository.

## Excluded

Add `docs/forge/` to `.gitignore`.

Use for solo work or when governance artifacts must stay local.

```gitignore
docs/forge/
```

## Companion Private Repository

Code lives in the public repo. Governance docs live in a private companion repo cloned nearby.

Use for public tools or projects that need internal process separated from the public artifact.

Choose the pattern that matches visibility, audit, and customer requirements.
