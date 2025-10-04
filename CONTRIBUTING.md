# Contributing to JarvisX

Thank you for your interest in contributing to JarvisX! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check if the issue already exists
2. Use the appropriate issue template
3. Provide clear steps to reproduce
4. Include relevant system information

### Feature Requests

We welcome feature requests! Please:
1. Check existing feature requests first
2. Describe the feature clearly
3. Explain the use case and benefits
4. Consider implementation complexity

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

## 🏗️ Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/your-username/jarvisx.git
cd jarvisx

# Install dependencies
npm install

# Set up environment
cp env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d

# Run tests
npm test
```

### Development Workflow

1. **Create a branch** for your feature/fix
2. **Write tests** first (TDD approach)
3. **Implement your changes**
4. **Run tests** to ensure nothing breaks
5. **Update documentation**
6. **Commit with clear messages**

## 📝 Coding Standards

### TypeScript/JavaScript

- Use ESLint configuration provided
- Follow the existing code style
- Use meaningful variable and function names
- Add JSDoc comments for public APIs
- Prefer `const` over `let`, avoid `var`

### Python

- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings for functions and classes
- Keep functions small and focused

### Git Commit Messages

Use conventional commits format:

```
type(scope): description

feat(auth): add JWT token refresh functionality
fix(stt): resolve audio file format validation issue
docs(readme): update installation instructions
test(orchestrator): add integration tests for task approval
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm test

# Run specific service tests
cd apps/orchestrator && npm test
cd services/stt && python -m pytest

# Run integration tests
npm run test:integration

# Run with coverage
npm run test:coverage
```

### Test Requirements

- **Unit tests**: Required for new functionality
- **Integration tests**: Required for service interactions
- **E2E tests**: Required for user-facing features
- **Coverage**: Maintain >80% test coverage

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Tests for service interactions
├── e2e/           # End-to-end workflow tests
└── fixtures/      # Test data and mock files
```

## 📚 Documentation

### Code Documentation

- **README**: Update for new features or setup changes
- **API Docs**: Document new endpoints and parameters
- **Inline Comments**: Explain complex logic and business rules
- **Type Definitions**: Keep TypeScript interfaces up to date

### Documentation Standards

- Use clear, concise language
- Include code examples where helpful
- Update related documentation when making changes
- Use markdown formatting consistently

## 🔒 Security

### Security Considerations

- **Never commit secrets** (API keys, passwords, tokens)
- **Validate all inputs** to prevent injection attacks
- **Use parameterized queries** for database operations
- **Implement proper authentication** for new endpoints
- **Follow principle of least privilege** for permissions

### Reporting Security Issues

For security vulnerabilities, please:
1. **Do not** create public issues
2. Email security concerns to: security@jarvisx.dev
3. Include steps to reproduce the issue
4. Wait for acknowledgment before public disclosure

## 🚀 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] Changelog updated
- [ ] Security scan completed
- [ ] Performance benchmarks met

## 📋 Code Review Process

### For Contributors

1. **Self-review** your PR before requesting review
2. **Add reviewers** from the maintainer team
3. **Respond to feedback** promptly and constructively
4. **Make requested changes** and update the PR
5. **Wait for approval** before merging

### For Reviewers

1. **Check functionality** and test the changes
2. **Review code quality** and adherence to standards
3. **Verify tests** are adequate and passing
4. **Check documentation** is updated appropriately
5. **Provide constructive feedback** with suggestions

## 🏷️ Labels and Milestones

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority: high`: High priority issue
- `priority: low`: Low priority issue

### Pull Request Labels

- `breaking-change`: Breaking API changes
- `needs-review`: Ready for review
- `needs-tests`: Requires additional tests
- `needs-docs`: Requires documentation updates

## 🤔 Getting Help

### Questions and Discussions

- **GitHub Discussions**: For general questions and ideas
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check the wiki for detailed guides

### Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others when you can
- Follow the code of conduct

## 📜 License

By contributing to JarvisX, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be:
- Listed in the CONTRIBUTORS.md file
- Mentioned in release notes for significant contributions
- Invited to join the core team for sustained contributions

---

Thank you for contributing to JarvisX! Your efforts help make AI assistance more accessible to Sinhala-speaking users worldwide. 🌟
