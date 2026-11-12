# Agent instructions

- Use the [`ponytail`](https://github.com/DietrichGebert/ponytail) skill for all coding work.
- Run `poetry run prek install` when you set up this repository. This installs the basic pre-commit checks.
- Run `poetry run prek run --all-files` regularly. Run it before pushing or creating a PR when those actions are authorized.
- Run `ponytail-audit` before every commit. Fix findings caused by the staged change before committing.
- Use conventional commits, keep commits focused and their messages concise.
- Write all documentation in Simplified Technical English (STE). Use short, active sentences and consistent terms. Give one instruction per sentence. Preserve exact commands and identifiers.
- If authorized to push, create a draft PR at first opportunity so CI can be utilized most effectively.
