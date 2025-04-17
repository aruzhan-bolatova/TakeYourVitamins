const { execSync } = require("child_process")

console.log("Installing shadcn/ui components...")

// Initialize shadcn/ui if not already initialized
try {
  execSync("npx shadcn@latest init", { stdio: "inherit" })
} catch (error) {
  console.log("shadcn/ui already initialized or initialization failed. Continuing with component installation...")
}

// List of components to install
const components = [
  "button",
  "card",
  "input",
  "label",
  "textarea",
  "select",
  "alert",
  "avatar",
  "badge",
  "calendar",
  "dropdown-menu",
  "popover",
  "alert-dialog",
  "separator",
  "tabs",
]

// Install each component
for (const component of components) {
  try {
    console.log(`Installing ${component}...`)
    execSync(`npx shadcn@latest add ${component}`, { stdio: "inherit" })
  } catch (error) {
    console.error(`Failed to install ${component}. Error: ${error.message}`)
  }
}

// Install additional dependencies
console.log("Installing additional dependencies...")
try {
  execSync("npm install date-fns lucide-react", { stdio: "inherit" })
} catch (error) {
  console.error(`Failed to install additional dependencies. Error: ${error.message}`)
}

console.log("Setup complete! All components and dependencies have been installed.")

