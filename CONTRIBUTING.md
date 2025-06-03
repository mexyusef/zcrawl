# Contributing to ZCrawl

Thank you for your interest in contributing to ZCrawl! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for ZCrawl.

#### Before Submitting A Bug Report

- Check the [issues](https://github.com/mexyusef/zcrawl/issues) to see if the problem has already been reported.
- Ensure you're using the latest version of ZCrawl.
- Collect information about your environment (OS, Python version, etc.).

#### How Do I Submit A Bug Report?

Bugs are tracked as [GitHub issues](https://github.com/mexyusef/zcrawl/issues).

Explain the problem and include additional details to help maintainers reproduce the problem:

- Use a clear and descriptive title.
- Describe the exact steps to reproduce the problem.
- Describe the behavior you observed after following the steps.
- Explain which behavior you expected to see instead and why.
- Include screenshots if possible.
- Include details about your environment.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for ZCrawl.

#### Before Submitting An Enhancement Suggestion

- Check if the enhancement has already been suggested or implemented.
- Ensure it aligns with the project's goals.

#### How Do I Submit An Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/mexyusef/zcrawl/issues).

- Use a clear and descriptive title.
- Provide a detailed description of the suggested enhancement.
- Explain why this enhancement would be useful.
- Include mockups or examples if applicable.

### Pull Requests

The process described here has several goals:

- Maintain ZCrawl's quality
- Fix problems that are important to users
- Enable a sustainable system for maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Run the tests to ensure they pass
5. Submit a pull request

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

#### Pull Request Guidelines

- Follow the [style guides](#style-guides)
- Include tests when adding new features
- Update documentation when changing the API
- Keep pull requests focused on a single topic
- Write a clear commit message

## Style Guides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use consistent code formatting with Black
- Sort imports with isort
- Add docstrings to all functions and classes

### Documentation Style Guide

- Use [Markdown](https://daringfireball.net/projects/markdown/) for documentation
- Reference functions and classes appropriately
- Update documentation when changing functionality

## Development Environment Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -e ".[dev]"`
5. Run the application: `python -m zcrawl`

## Running Tests

```bash
pytest
```

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

- `bug` - Issues that are bugs
- `enhancement` - Issues that are feature requests
- `documentation` - Issues or PRs related to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed

Thank you for contributing to ZCrawl!
