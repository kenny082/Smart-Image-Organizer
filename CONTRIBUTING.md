# Contributing to Smart Image Organizer

This document provides guidelines and setup instructions for developing Smart Image Organizer.

## Development Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/kenny082/Smart-Image-Organizer.git
cd Smart-Image-Organizer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies and set up pre-commit hooks:
```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt
pip install -e .
pre-commit install
```

This will set up pre-commit hooks that run automatically on `git commit` to:
- Format code with black
- Sort imports with isort
- Check types with mypy
- Lint with flake8 (including docstring checks)
- Check for common issues (trailing whitespace, large files, etc.)

## Development Tools

The project uses several development tools:

- **pytest**: For running tests
- **black**: For code formatting
- **flake8**: For code linting
- **mypy**: For type checking
- **coverage**: For test coverage reporting

### Running Tests

Run tests with coverage:
```bash
PYTHONPATH=$PYTHONPATH:/path/to/Smart-Image-Organizer pytest tests/
```

### Code Quality Checks

Format code:
```bash
black src/ tests/
```

Run linter:
```bash
flake8 src/ tests/
```

Run type checker:
```bash
mypy src/ tests/
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

1. **tests.yml**: Runs tests on Python 3.8-3.11
2. **code-quality.yml**: Runs formatting, linting, and type checks
3. **publish.yml**: Builds and publishes to PyPI on releases

### Coverage Reports

Coverage reports are uploaded to Codecov after each test run. The target coverage is 80%.

## Project Structure

```
Smart-Image-Organizer/
├── src/               # Main code
│   ├── ai_tagger.py        # AI-powered image tagging
│   ├── cli.py             # Command-line interface
│   ├── exif_handler.py    # EXIF metadata extraction
│   ├── file_organizer.py  # Core file organization logic
│   └── geolocation.py     # Geolocation handling
├── tests/             # Test suite
│   ├── test_ai_tagger.py
│   ├── test_cli.py
│   ├── test_exif_handler.py
│   ├── test_file_organizer.py
│   └── test_geolocation.py
├── .github/          # GitHub Actions workflows
├── .gitignore       # Git ignore rules
├── README.md        # Project documentation
├── CONTRIBUTING.md  # Contribution guidelines
├── requirements.txt # Production dependencies
├── dev-requirements.txt  # Development dependencies
├── setup.py        # Package setup
├── pyproject.toml  # Project configuration
└── .codecov.yml    # Codecov configuration
```

## Making Changes

1. Create a new branch for your changes
2. Make your changes
3. Add tests for new functionality
4. Run tests and quality checks
5. Commit changes with descriptive messages
6. Push changes and create a pull request

## Commit Message Format

Use descriptive commit messages that explain what the change does:

```
Added improved CLI with progress bars and preview command
- Added proper progress bars with time estimation
- Added preview command to show planned operations
- Added better error handling
- Added comprehensive tests
```

## Need Help?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about the codebase
- Development environment issues
