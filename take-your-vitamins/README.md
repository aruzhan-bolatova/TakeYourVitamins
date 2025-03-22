This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

### Quick Start (Recommended)

1. Make sure you have `make` installed on your system:
   - On macOS: `brew install make`
   - On Linux: `sudo apt-get install make` (Ubuntu/Debian) or `sudo yum install make` (Fedora)
   - On Windows: Install via [Chocolatey](https://chocolatey.org/) with `choco install make`

2. Run the setup command:
```bash
make setup
```

This will:
- Install all project dependencies
- Initialize shadcn/ui
- Install all required UI components
- Install the correct SWC dependencies for your system (automatically detected)

3. Start the development server:
```bash
make dev
```

### Available Make Commands

- `make setup` - Set up the project (install dependencies and initialize shadcn/ui)
- `make install` - Install dependencies
- `make dev` - Start development server
- `make clean` - Clean build artifacts and dependencies
- `make reset` - Reset the project (clean and setup, useful for completely resetting the project)
- `make lint` - Run linter
- `make build` - Build for production
- `make start` - Start production server
- `make fix` - Fix the searchParams issue in search-results page
- `make help` - Show available commands

### Troubleshooting

If you encounter any issues:

1. For SWC dependency issues:
   ```bash
   make reset
   ```
   The Makefile will automatically detect your system and install the correct SWC dependencies.

2. For the searchParams error in the search-results page:
   ```bash
   make fix
   ```

### Manual Setup

If you prefer to set up the project manually, follow these steps:

First, install the dependencies:

```bash
npm install
```

Then, initialize shadcn/ui if not already initialized:

```bash
npx shadcn@latest init
```

Then install UI components:
```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add textarea
npx shadcn@latest add select
npx shadcn@latest add alert
npx shadcn@latest add avatar
npx shadcn@latest add badge
npx shadcn@latest add calendar
npx shadcn@latest add dropdown-menu
npx shadcn@latest add popover
npx shadcn@latest add alert-dialog
npx shadcn@latest add separator
npx shadcn@latest add tabs
npx shadcn@latest add switch
npx shadcn@latest add slider
```

If you see a warning about missing SWC dependencies, run:
```bash
npm install
```

Finally, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result. If port 3000 is in use, the server will automatically use the next available port (e.g., 3001).

## Project Structure

This is a Next.js application that helps users track their vitamin and supplement intake. It includes:

- User authentication
- Supplement tracking
- Symptom logging
- Calendar integration
- Responsive UI with shadcn/ui components

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
- [shadcn/ui Documentation](https://ui.shadcn.com) - learn about the UI components used in this project.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
