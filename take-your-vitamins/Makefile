.PHONY: setup install dev clean lint build start help reset fix

# Default target
all: setup

# Setup the project (install dependencies and initialize shadcn/ui)
setup: install
	@echo "🚀 Setting up shadcn/ui..."
	@if [ -f components.json ]; then \
		echo "📝 components.json already exists, skipping initialization..."; \
	else \
		npx shadcn@latest init -y; \
	fi
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
	@echo "🔧 Fixing SWC dependencies..."
	@if [ "$(shell uname)" = "Darwin" ]; then \
		if [ "$(shell uname -m)" = "arm64" ]; then \
			npm install @next/swc-darwin-arm64; \
		else \
			npm install @next/swc-darwin-x64; \
		fi \
	elif [ "$(shell uname)" = "Linux" ]; then \
		if [ "$(shell uname -m)" = "aarch64" ]; then \
			npm install @next/swc-linux-arm64-gnu; \
		else \
			npm install @next/swc-linux-x64-gnu; \
		fi \
	elif [ "$(shell uname)" = "MINGW"* ] || [ "$(shell uname)" = "MSYS"* ]; then \
		if [ "$(shell uname -m)" = "x86_64" ]; then \
			npm install @next/swc-win32-x64-msvc; \
		elif [ "$(shell uname -m)" = "aarch64" ]; then \
			npm install @next/swc-win32-arm64-msvc; \
		else \
			npm install @next/swc-win32-ia32-msvc; \
		fi \
	fi

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
	@rm -f components.json

# Reset the project (clean and setup)
reset: clean setup

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

# Fix searchParams issue
fix:
	@echo "🔧 Fixing searchParams issue..."
	@if [ "$(shell uname)" = "Darwin" ]; then \
		sed -i '' 's/const query = searchParams.q || ""/const query = await Promise.resolve(searchParams.q || "")/' app/search-results/page.tsx; \
	else \
		sed -i 's/const query = searchParams.q || ""/const query = await Promise.resolve(searchParams.q || "")/' app/search-results/page.tsx; \
	fi

# Help command
help:
	@echo "Available commands:"
	@echo "  make setup    - Set up the project (install dependencies and initialize shadcn/ui)"
	@echo "  make install  - Install dependencies"
	@echo "  make dev      - Start development server"
	@echo "  make clean    - Clean build artifacts and dependencies"
	@echo "  make reset    - Reset the project (clean and setup)"
	@echo "  make lint     - Run linter"
	@echo "  make build    - Build for production"
	@echo "  make start    - Start production server"
	@echo "  make fix      - Fix the searchParams issue in search-results page"
	@echo "  make help     - Show this help message" 