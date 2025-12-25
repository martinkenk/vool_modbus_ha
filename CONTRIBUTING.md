# Contributing to VOOL Modbus Integration

Thank you for considering contributing to the VOOL Modbus integration! This document outlines the guidelines for contributing.

## How to Contribute

### Reporting Bugs

1. Check if the issue has already been reported in the [Issues](https://github.com/martinkenk/vool-modbus-ha/issues)
2. If not, create a new issue with:
   - A clear, descriptive title
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - Home Assistant version and integration version
   - Relevant logs (with sensitive info redacted)

### Suggesting Features

1. Open an issue with the "Feature Request" template
2. Describe the feature and its use case
3. Explain how it would benefit users

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes following our code style
4. Write/update tests if applicable
5. Update documentation if needed
6. Commit with clear messages: `git commit -m "Add feature X"`
7. Push to your fork: `git push origin feature/my-feature`
8. Open a Pull Request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/martinkenk/vool-modbus-ha.git
   cd vool-modbus-ha
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements_dev.txt
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for public functions
- Keep functions small and focused
- Use meaningful variable names

## Testing

Run tests with:
```bash
pytest tests/
```

## Questions?

Open a discussion or reach out through the issue tracker.

Thank you for contributing! 🎉
