.PHONY: setup install dev clean lint build

# Default target
all: setup

# Setup the project (install dependencies and initialize shadcn/ui)
setup: install
	@echo "🚀 Setting up shadcn/ui..."
	@npx shadcn@latest init -y
	@echo "📦 Installing UI components..."
	@npx shadcn@latest add button -y
	@npx shadcn@latest add card -y
	@npx shadcn@latest add input -y
	@npx shadcn@latest add label -y
	@npx shadcn@latest add textarea -y
	@npx shadcn@latest add select -y
	@npx shadcn@latest add alert -y
	@npx shadcn@latest add avatar -y
	@npx shadcn@latest add badge -y
	@npx shadcn@latest add calendar -y
	@npx shadcn@latest add dropdown-menu -y
	@npx shadcn@latest add popover -y
	@npx shadcn@latest add alert-dialog -y
	@npx shadcn@latest add separator -y
	@npx shadcn@latest add tabs -y
	@npx shadcn@latest add switch -y
	@npx shadcn@latest add slider -y
	@echo "✅ Setup complete!"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@npm install

# Start development server
dev:
	@echo "🚀 Starting development server..."
	@npm run dev

# Clean build artifacts and dependencies
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf .next
	@rm -rf node_modules
	@rm -f package-lock.json

# Run linter
lint:
	@echo "🔍 Running linter..."
	@npm run lint

# Build for production
build:
	@echo "🏗️ Building for production..."
	@npm run build

# Start production server
start:
	@echo "🚀 Starting production server..."
	@npm run start

# Help command
help:
	@echo "Available commands:"
	@echo "  make setup    - Set up the project (install dependencies and initialize shadcn/ui)"
	@echo "  make install  - Install dependencies"
	@echo "  make dev      - Start development server"
	@echo "  make clean    - Clean build artifacts and dependencies"
	@echo "  make lint     - Run linter"
	@echo "  make build    - Build for production"
	@echo "  make start    - Start production server"
	@echo "  make help     - Show this help message" 