/**
 * Frontend generator script.
 * Maps UI JSON -> React (Vite dev) + Next.js deployable static pages.
 * Outputs bundle.zip
 */
const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');

const [uiJsonPath, outputDir] = process.argv.slice(2);

if (!uiJsonPath || !outputDir) {
  console.error('Usage: node generate.js <ui-json-path> <output-dir>');
  process.exit(1);
}

async function generate() {
  try {
    // Read UI JSON
    const uiJson = JSON.parse(await fs.readFile(uiJsonPath, 'utf-8'));
    
    // Create Next.js structure
    const pagesDir = path.join(outputDir, 'pages');
    const publicDir = path.join(outputDir, 'public');
    const stylesDir = path.join(outputDir, 'styles');
    
    await fs.ensureDir(pagesDir);
    await fs.ensureDir(publicDir);
    await fs.ensureDir(stylesDir);
    
    // Generate package.json
    const packageJson = {
      name: `resume-${path.basename(outputDir)}`,
      version: '1.0.0',
      scripts: {
        dev: 'next dev',
        build: 'next build',
        export: 'next export'
      },
      dependencies: {
        next: '^14.0.0',
        react: '^18.0.0',
        'react-dom': '^18.0.0',
        tailwindcss: '^3.3.0',
        autoprefixer: '^10.4.16',
        postcss: '^8.4.31'
      }
    };
    await fs.writeJson(path.join(outputDir, 'package.json'), packageJson, { spaces: 2 });
    
    // Generate next.config.js
    const nextConfig = `module.exports = {
  output: 'export',
  images: {
    unoptimized: true
  }
}`;
    await fs.writeFile(path.join(outputDir, 'next.config.js'), nextConfig);
    
    // Generate tailwind.config.js
    const tailwindConfig = `module.exports = {
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '${uiJson.theme?.primaryColor || '#3b82f6'}',
        secondary: '${uiJson.theme?.secondaryColor || '#1e40af'}',
      },
      fontFamily: {
        sans: ['${uiJson.theme?.fontFamily || 'Inter'}', 'sans-serif'],
      },
    },
  },
  plugins: [],
}`;
    await fs.writeFile(path.join(outputDir, 'tailwind.config.js'), tailwindConfig);
    
    // Generate postcss.config.js
    const postcssConfig = `module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}`;
    await fs.writeFile(path.join(outputDir, 'postcss.config.js'), postcssConfig);
    
    // Generate global CSS
    const globalCss = `@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: ${uiJson.theme?.fontFamily || 'Inter, sans-serif'};
}`;
    await fs.writeFile(path.join(stylesDir, 'globals.css'), globalCss);
    
    // Generate _app.js
    const appJs = `import '../styles/globals.css';

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />;
}`;
    await fs.writeFile(path.join(pagesDir, '_app.js'), appJs);
    
    // Generate index.js (main resume page)
    const indexJs = generateIndexPage(uiJson);
    await fs.writeFile(path.join(pagesDir, 'index.js'), indexJs);
    
    // Generate index.html (for preview)
    const indexHtml = generateIndexHtml(uiJson);
    await fs.writeFile(path.join(outputDir, 'index.html'), indexHtml);
    
    console.log(`Frontend bundle generated successfully at ${outputDir}`);
  } catch (error) {
    console.error('Error generating frontend:', error);
    process.exit(1);
  }
}

function generateIndexPage(uiJson) {
  const sections = uiJson.sections || [];
  
  return `import React from 'react';
import Head from 'next/head';

export default function Resume() {
  const uiData = ${JSON.stringify(uiJson, null, 2)};
  
  return (
    <>
      <Head>
        <title>Resume</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8">
          ${sections.map(section => renderSection(section)).join('\n          ')}
        </div>
      </div>
    </>
  );
}

${generateSectionComponents()}
`;
}

function renderSection(section) {
  const type = section.type;
  const content = section.content || {};
  
  switch (type) {
    case 'header':
      return `<HeaderSection content={${JSON.stringify(content)}} />`;
    case 'summary':
      return `<SummarySection content="${content}" />`;
    case 'experience':
      return `<ExperienceSection content={${JSON.stringify(content)}} />`;
    case 'education':
      return `<EducationSection content={${JSON.stringify(content)}} />`;
    case 'skills':
      return `<SkillsSection content={${JSON.stringify(content)}} />`;
    default:
      return `<div className="mb-6"><pre>${JSON.stringify(section, null, 2)}</pre></div>`;
  }
}

function generateSectionComponents() {
  return `
function HeaderSection({ content }) {
  return (
    <header className="text-center mb-8 pb-8 border-b-2 border-gray-200">
      <h1 className="text-4xl font-bold text-primary mb-2">{content.name || ''}</h1>
      <p className="text-xl text-gray-600 mb-4">{content.title || ''}</p>
      {content.contact && (
        <div className="flex justify-center gap-4 text-sm">
          <span>{content.contact.email || ''}</span>
          <span>{content.contact.phone || ''}</span>
        </div>
      )}
    </header>
  );
}

function SummarySection({ content }) {
  return (
    <section className="mb-6">
      <p className="text-gray-700 leading-relaxed">{content}</p>
    </section>
  );
}

function ExperienceSection({ content }) {
  return (
    <section className="mb-6">
      <h2 className="text-2xl font-bold text-primary mb-4">{content.title || 'Experience'}</h2>
      {content.items && content.items.map((item, idx) => (
        <div key={idx} className="mb-4">
          <h3 className="text-xl font-semibold">{item.title || ''}</h3>
          <p className="text-gray-600">{item.company || ''} | {item.period || ''}</p>
          <p className="text-gray-700 mt-2">{item.description || ''}</p>
        </div>
      ))}
    </section>
  );
}

function EducationSection({ content }) {
  return (
    <section className="mb-6">
      <h2 className="text-2xl font-bold text-primary mb-4">{content.title || 'Education'}</h2>
      {content.items && content.items.map((item, idx) => (
        <div key={idx} className="mb-4">
          <h3 className="text-xl font-semibold">{item.degree || ''}</h3>
          <p className="text-gray-600">{item.school || ''} | {item.year || ''}</p>
        </div>
      ))}
    </section>
  );
}

function SkillsSection({ content }) {
  return (
    <section className="mb-6">
      <h2 className="text-2xl font-bold text-primary mb-4">{content.title || 'Skills'}</h2>
      <div className="flex flex-wrap gap-2">
        {content.items && content.items.map((skill, idx) => (
          <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
            {skill}
          </span>
        ))}
      </div>
    </section>
  );
}
`;
}

function generateIndexHtml(uiJson) {
  const theme = uiJson.theme || {};
  const sections = uiJson.sections || [];
  
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Resume Preview</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { font-family: ${theme.fontFamily || 'Inter, sans-serif'}; }
    .primary-color { color: ${theme.primaryColor || '#3b82f6'}; }
  </style>
</head>
<body class="bg-gray-50 p-8">
  <div class="max-w-4xl mx-auto bg-white shadow-lg p-8">
    ${sections.map(s => renderHtmlSection(s)).join('\n    ')}
  </div>
</body>
</html>`;
}

function renderHtmlSection(section) {
  const type = section.type;
  const content = section.content || {};
  
  switch (type) {
    case 'header':
      return `<header class="text-center mb-8 pb-8 border-b-2 border-gray-200">
      <h1 class="text-4xl font-bold primary-color mb-2">${content.name || ''}</h1>
      <p class="text-xl text-gray-600 mb-4">${content.title || ''}</p>
      <div class="flex justify-center gap-4 text-sm">
        <span>${content.contact?.email || ''}</span>
        <span>${content.contact?.phone || ''}</span>
      </div>
    </header>`;
    case 'summary':
      return `<section class="mb-6">
      <p class="text-gray-700 leading-relaxed">${content}</p>
    </section>`;
    case 'experience':
      const expItems = (content.items || []).map(item => `
      <div class="mb-4">
        <h3 class="text-xl font-semibold">${item.title || ''}</h3>
        <p class="text-gray-600">${item.company || ''} | ${item.period || ''}</p>
        <p class="text-gray-700 mt-2">${item.description || ''}</p>
      </div>`).join('');
      return `<section class="mb-6">
      <h2 class="text-2xl font-bold primary-color mb-4">${content.title || 'Experience'}</h2>
      ${expItems}
    </section>`;
    case 'education':
      const eduItems = (content.items || []).map(item => `
      <div class="mb-4">
        <h3 class="text-xl font-semibold">${item.degree || ''}</h3>
        <p class="text-gray-600">${item.school || ''} | ${item.year || ''}</p>
      </div>`).join('');
      return `<section class="mb-6">
      <h2 class="text-2xl font-bold primary-color mb-4">${content.title || 'Education'}</h2>
      ${eduItems}
    </section>`;
    case 'skills':
      const skillItems = (content.items || []).map(skill => `
        <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">${skill}</span>`).join('');
      return `<section class="mb-6">
      <h2 class="text-2xl font-bold primary-color mb-4">${content.title || 'Skills'}</h2>
      <div class="flex flex-wrap gap-2">
        ${skillItems}
      </div>
    </section>`;
    default:
      return `<div class="mb-6"><pre>${JSON.stringify(section, null, 2)}</pre></div>`;
  }
}

generate();

