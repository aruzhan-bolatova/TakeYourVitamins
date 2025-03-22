#!/bin/bash

# Install shadcn/ui components
echo "Installing shadcn/ui components..."

# Initialize shadcn/ui if not already initialized
npx shadcn@latest init

# Install UI components
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

# Install additional dependencies
echo "Installing additional dependencies..."
npm install date-fns lucide-react

echo "Setup complete! All components and dependencies have been installed."

