# CI/CD Pipeline

This project uses GitHub Actions for continuous integration and delivery. The pipeline includes the following steps:

## Features

- **Test Coverage**: Runs tests on Python 3.11 and 3.12
- **Code Quality**: Flake8 linting and style checks
- **Security Scanning**: Bandit security scan and Safety dependency check
- **Docker Build**: Builds and pushes Docker image to Docker Hub
- **Deployment**: Production deployment trigger on release

## Pipeline Workflow

**File**: [`.github/workflows/main.yml`](../.github/workflows/main.yml)

| Job | Description | Triggers |
|-----|-------------|----------|
| `test` | Runs tests with coverage on Python 3.11 and 3.12 | Push to main/develop, PRs, releases |
| `lint` | Lints code with Flake8 | Push to main/develop, PRs, releases |
| `security` | Runs Bandit and Safety scans | Push to main/develop, PRs, releases |
| `build` | Builds and pushes Docker image | Releases or main branch pushes |
| `deploy` | Deploys to production | Releases only |

## Secrets Required

Add these secrets to your GitHub repository settings:

- `DOCKER_HUB_USERNAME`: Docker Hub username
- `DOCKER_HUB_TOKEN`: Docker Hub access token

## Docker Image Tags

The pipeline builds and pushes images with:

- Semantic versioning tags (e.g., `v1.0.0`, `v1.0`)
- Branch name tags (e.g., `main`, `develop`)
- SHA commit tags (e.g., `sha-abc123`)
- `latest` tag (for main branch)
