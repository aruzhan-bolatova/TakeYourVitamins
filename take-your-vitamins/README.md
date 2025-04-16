# TakeYourVitamins: Project Front-End Setup and Usage Guide

## Demo Video: https://www.youtube.com/watch?v=pZ5-YR11N0U 

## Prerequisites
Before running this project, ensure you have the following installed:
- Node.js (Latest LTS recommended)
- npm (Comes with Node.js)
- `make` (Available on macOS/Linux by default; Windows users may need to install Make through Git Bash or WSL)

## Installation and Setup
To set up the project, run:
```sh
make setup
```
This will:
1. Install dependencies.
2. Initialize `shadcn/ui`.
3. Add required UI components.

## Available Commands
The following `make` commands are available:

### 1. Install Dependencies
```sh
make install
```
Installs all necessary dependencies for the project.

### 2. Start Development Server
```sh
make dev
```
Starts the development server for local testing.

### 3. Clean Project
```sh
make clean
```
Removes all generated files including:
- `.next` (Build artifacts)
- `node_modules`
- `package-lock.json`
- `components.json`

### 4. Reset Project
```sh
make reset
```
Runs `make clean` and `make setup` to reset the project to a fresh state.

### 5. Run Linter
```sh
make lint
```
Runs the linter to check for code issues.

### 6. Build for Production
```sh
make build
```
Compiles the project for production deployment.

### 7. Start Production Server
```sh
make start
```
Runs the production build of the project.

### 8. Fix `searchParams` Issue
```sh
make fix
```
Fixes a known issue with `searchParams` in `app/search-results/page.tsx`.

### 9. Display Help
```sh
make help
```
Shows a list of available commands.

## Notes
- Windows users should use Git Bash, WSL, or a compatible terminal that supports `make`.
- Ensure you have network access to install dependencies and UI components.
- If you encounter issues, try running `make reset` to start fresh.

Happy coding! 🚀

