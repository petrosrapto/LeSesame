# Contributing to Le Sésame

Thank you for your interest in contributing! This document explains how to get involved.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** from `main` for your changes
4. **Make your changes** and ensure all tests pass
5. **Submit a pull request** targeting the `main` branch

## Development Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Pull Request Guidelines

- All PRs must target the `main` branch
- PRs require approval from the repository owner before merging
- All CI checks (linting, tests, build) must pass
- Keep PRs focused — one feature or fix per PR
- Write a clear description of what the PR does and why

## Code Standards

- **Backend:** Follow existing Python code style. Run `pytest` before submitting.
- **Frontend:** Run `npm run lint` and `npm run test` before submitting.
- Do not commit `.env` files or any secrets/credentials.

## Reporting Issues

- Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) template for bugs
- Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) template for ideas
- For security vulnerabilities, see [SECURITY.md](SECURITY.md) — **do not open a public issue**

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
