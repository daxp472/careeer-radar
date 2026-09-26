# Contributing to CareerRadar

Thank you for your interest in contributing to **CareerRadar**! We welcome contributions ranging from bug fixes and documentation improvements to new skill extraction heuristics.

---

## 🛠️ Development Setup

1. **Fork and Clone** the repository:
   ```bash
   git clone https://github.com/daxp472/careeer-radar.git
   cd careeer-radar
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🧪 Running Tests

Before submitting a Pull Request, ensure that all test suites and builds pass cleanly:

- **Backend Pytest Suite**:
  ```bash
  cd backend
  pytest -v
  ```
- **Frontend Build & TypeScript Checks**:
  ```bash
  cd frontend
  npm run build
  ```

---

## 📐 Git Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(scope): ...` for new features
- `fix(scope): ...` for bug fixes
- `docs(scope): ...` for documentation changes
- `refactor(scope): ...` for code refactoring
- `test(scope): ...` for adding or updating tests
- `chore(scope): ...` for maintenance and config tasks

---

## 🚀 Pull Request Workflow

1. Create a feature branch: `git checkout -b feat/your-feature-name`
2. Make changes, ensuring coding standards and comments are maintained.
3. Run the full test suite (`pytest` and `npm run build`).
4. Commit your changes with descriptive messages.
5. Push to your fork and submit a PR to the `main` branch.
