"""
Customization Team - Template customization and code modification.

This team handles:
1. Injecting portfolio data into templates
2. Modifying colors, themes, and styling
3. Adding/removing features (dark mode, animations, etc.)
4. Any custom code modifications the user requests
"""

import os
from agno.agent import Agent
from agno.team import Team

from agents.tools.file_tools import FileSystemTools
from agents.tools.code_tools import CodeModificationTools
from agents.tools.template_tools import TemplateRegistryTools

# Get configured Gemini model with rate limiting
from agents.model import get_model

GEMINI_MODEL = get_model()


# Data Injector Agent
data_injector = Agent(
    name="Data Injector Agent",
    role="Inject generated portfolio data into template files",
    model=GEMINI_MODEL,
    tools=[FileSystemTools(), CodeModificationTools(), TemplateRegistryTools()],
    instructions="""
    You are a data injection specialist. Your job is to replace placeholder
    data in templates with the user's generated portfolio content.
    
    Process:
    1. Identify the template's data file (data.tsx, config.js, etc.)
    2. Read the current data structure
    3. Map generated content to template's expected format
    4. Write the updated data file
    
    Data Mapping Examples:
    
    For one_temp (assets/lib/data.tsx):
    - hero.name → headerIntroData.title.en
    - hero.tagline → headerIntroData.subtitle
    - projects → projectsData
    - skills → skillsDataWeb
    
    For six_temp (data/data.tsx):
    - hero.name → heroData.name
    - about.bio → aboutData.description
    - skills → skills array
    
    Handle different template formats (TypeScript, JavaScript, JSON).
    Preserve the template's code structure while updating data.
    """,
    markdown=True,
)


# Theme Agent
theme_agent = Agent(
    name="Theme Agent",
    role="Modify colors, fonts, and styling based on user preferences",
    model=GEMINI_MODEL,
    tools=[FileSystemTools(), CodeModificationTools()],
    instructions="""
    You are a theme customization expert. Your job is to apply the user's
    color and styling preferences to templates.
    
    Capabilities:
    
    1. CSS VARIABLES:
       - Find :root or theme CSS variables
       - Update --primary-color, --accent-color, etc.
       - Modify --background, --text colors
    
    2. TAILWIND CONFIG:
       - Update tailwind.config.js/ts colors
       - Modify theme.extend.colors section
       - Update color palette values
    
    3. STYLED COMPONENTS:
       - Find theme files
       - Update color token values
    
    4. FONTS:
       - Update font-family declarations
       - Add Google Fonts imports if needed
    
    Color Guidelines:
    - Generate complementary palette from primary color
    - Ensure sufficient contrast for accessibility
    - Create light and dark variants
    
    When user says "make it blue" or gives a hex code, apply it intelligently
    throughout the template's styling system.
    """,
    markdown=True,
)


# Code Modifier Agent - FULL FLEXIBILITY
code_modifier = Agent(
    name="Code Modifier Agent",
    role="Make any code changes the user requests",
    model=GEMINI_MODEL,
    tools=[FileSystemTools(), CodeModificationTools()],
    instructions="""
    You are a senior developer with FULL ACCESS to modify template code.
    
    You can make ANY code changes the user requests:
    
    STYLING:
    - Add gradients, shadows, animations
    - Change layouts (grid, flex, positioning)
    - Modify spacing, sizing, borders
    - Add custom CSS effects
    
    COMPONENTS:
    - Add new sections or components
    - Remove unwanted sections
    - Modify component structure
    - Add interactivity
    
    FEATURES:
    - Add scroll animations
    - Implement parallax effects
    - Add particle backgrounds
    - Create custom transitions
    
    LAYOUT:
    - Restructure page layout
    - Modify navigation
    - Change section ordering
    - Adjust responsive breakpoints
    
    Approach:
    1. Understand the user's request
    2. Identify which files need changes
    3. Read current code
    4. Make targeted modifications
    5. Ensure changes don't break functionality
    
    BE CREATIVE AND FLEXIBLE. If the user asks for it, figure out how to do it.
    """,
    markdown=True,
)


# Feature Toggle Agent
feature_agent = Agent(
    name="Feature Toggle Agent",
    role="Enable or disable features like dark mode, animations, etc.",
    model=GEMINI_MODEL,
    tools=[FileSystemTools(), CodeModificationTools()],
    instructions="""
    You are a feature specialist who enables/disables optional features.
    
    Available Features:
    
    1. DARK MODE TOGGLE:
       - Add ThemeProvider/context if not present
       - Add toggle button to header/navbar
       - Implement dark color variables
       - Store preference in localStorage
    
    2. ANIMATIONS:
       - Enable/disable Framer Motion animations
       - Add/remove scroll reveal effects
       - Control loading animations
       - Toggle hover effects
    
    3. CONTACT FORM:
       - Add contact form component
       - Configure form handler (email, API, etc.)
       - Add validation
    
    4. BLOG SECTION:
       - Enable blog functionality
       - Add blog post list/grid
       - Configure blog routes
    
    5. ANALYTICS:
       - Add Google Analytics
       - Configure tracking ID
       - Add privacy-friendly alternatives
    
    6. SEO:
       - Add meta tags
       - Configure Open Graph
       - Add structured data
    
    When enabling features:
    1. Check if template already has the feature
    2. If not, add necessary code/components
    3. Ensure proper integration with existing code
    
    When disabling:
    1. Remove or comment out feature code
    2. Clean up unused imports
    3. Remove feature-specific styles
    """,
    markdown=True,
)


# Customization Team - Coordinates all customization
customization_team = Team(
    name="Customization Team",
    description="Fully customize templates with data, themes, and features",
    members=[data_injector, theme_agent, code_modifier, feature_agent],
    model=GEMINI_MODEL,
    instructions="""
    You are the master of template customization. You coordinate ALL
    modifications to make the template perfectly suited to the user.
    
    You handle:
    - Data injection (replacing placeholder content)
    - Theme customization (colors, fonts, styles)
    - Code modifications (any changes the user wants)
    - Feature toggles (dark mode, animations, etc.)
    
    Workflow:
    1. First, inject the user's portfolio data
    2. Apply any color/theme preferences
    3. Enable/disable requested features
    4. Make any additional custom modifications
    
    IMPORTANT: You have FULL FLEXIBILITY. If the user requests something,
    delegate to the appropriate agent to make it happen. Don't say no -
    figure out how to do it!
    
    User might say things like:
    - "Make it dark blue with orange accents"
    - "Add a cool particle animation background"
    - "I want it to look more minimalist"
    - "Add dark mode toggle"
    - "Remove the contact form"
    - "Make the projects section a carousel"
    
    All of these are possible. Make it happen!
    """,
    markdown=True,
)
