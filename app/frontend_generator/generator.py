"""
Frontend generator that creates React/Vite dev bundle and Next.js static export.
"""
import os
import json
import zipfile
import subprocess
import shutil
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import Artifact


def generate_frontend_bundle(job_id: int, ui_json: Dict[str, Any], db: Session) -> str:
    """
    Generate frontend bundle from UI JSON.
    Returns path to bundle.zip file.
    """
    generator_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend_generator")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "generated", str(job_id))
    bundles_dir = os.path.join(os.path.dirname(__file__), "..", "..", "bundles")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(bundles_dir, exist_ok=True)
    
    # Save UI JSON
    ui_json_path = os.path.join(output_dir, "ui.json")
    with open(ui_json_path, "w") as f:
        json.dump(ui_json, f, indent=2)
    
    # Call Node.js generator script
    generator_script = os.path.join(generator_dir, "generate.js")
    if os.path.exists(generator_script):
        try:
            result = subprocess.run(
                ["node", generator_script, ui_json_path, output_dir],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Generator output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Generator error: {e.stderr}")
            # Fallback: create minimal bundle
            _create_fallback_bundle(output_dir, ui_json)
    else:
        # Fallback: create minimal bundle
        _create_fallback_bundle(output_dir, ui_json)
    
    # Create bundle.zip
    bundle_path = os.path.join(bundles_dir, f"{job_id}_bundle.zip")
    _create_zip_bundle(output_dir, bundle_path)
    
    # Save artifact record
    artifact = Artifact(
        job_id=job_id,
        artifact_type="frontend_bundle",
        file_path=bundle_path,
        file_url=f"/api/v1/bundles/{job_id}_bundle.zip"
    )
    db.add(artifact)
    db.commit()
    
    return bundle_path


def _create_fallback_bundle(output_dir: str, ui_json: Dict[str, Any]):
    """Create a minimal fallback bundle if generator script fails."""
    # Create basic Next.js structure
    pages_dir = os.path.join(output_dir, "pages")
    public_dir = os.path.join(output_dir, "public")
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)
    
    # Generate index.html (for preview)
    index_html = _generate_index_html(ui_json)
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(index_html)
    
    # Generate Next.js pages/index.js
    index_js = _generate_nextjs_index(ui_json)
    with open(os.path.join(pages_dir, "index.js"), "w") as f:
        f.write(index_js)
    
    # Create package.json
    package_json = {
        "name": f"resume-{os.path.basename(output_dir)}",
        "version": "1.0.0",
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "export": "next export"
        },
        "dependencies": {
            "next": "^14.0.0",
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        }
    }
    with open(os.path.join(output_dir, "package.json"), "w") as f:
        json.dump(package_json, f, indent=2)
    
    # Create next.config.js
    next_config = """
module.exports = {
  output: 'export',
  images: {
    unoptimized: true
  }
}
"""
    with open(os.path.join(output_dir, "next.config.js"), "w") as f:
        f.write(next_config)


def _generate_index_html(ui_json: Dict[str, Any]) -> str:
    """Generate HTML preview from UI JSON."""
    theme = ui_json.get("theme", {})
    sections = ui_json.get("sections", [])
    
    primary_color = theme.get("primaryColor", "#3b82f6")
    font_family = theme.get("fontFamily", "Inter, sans-serif")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Preview</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: {font_family}; }}
        .primary-color {{ color: {primary_color}; }}
    </style>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-4xl mx-auto bg-white shadow-lg p-8">
"""
    
    for section in sections:
        section_type = section.get("type", "")
        content = section.get("content", {})
        
        if section_type == "header":
            html += f"""
        <header class="text-center mb-8 pb-8 border-b-2 border-gray-200">
            <h1 class="text-4xl font-bold primary-color mb-2">{content.get('name', '')}</h1>
            <p class="text-xl text-gray-600 mb-4">{content.get('title', '')}</p>
            <div class="flex justify-center gap-4 text-sm">
                <span>{content.get('contact', {}).get('email', '')}</span>
                <span>{content.get('contact', {}).get('phone', '')}</span>
            </div>
        </header>
"""
        elif section_type == "summary":
            html += f"""
        <section class="mb-6">
            <p class="text-gray-700 leading-relaxed">{content}</p>
        </section>
"""
        elif section_type == "experience":
            html += f"""
        <section class="mb-6">
            <h2 class="text-2xl font-bold primary-color mb-4">{content.get('title', 'Experience')}</h2>
"""
            for item in content.get("items", []):
                html += f"""
            <div class="mb-4">
                <h3 class="text-xl font-semibold">{item.get('title', '')}</h3>
                <p class="text-gray-600">{item.get('company', '')} | {item.get('period', '')}</p>
                <p class="text-gray-700 mt-2">{item.get('description', '')}</p>
            </div>
"""
            html += """
        </section>
"""
        elif section_type == "education":
            html += f"""
        <section class="mb-6">
            <h2 class="text-2xl font-bold primary-color mb-4">{content.get('title', 'Education')}</h2>
"""
            for item in content.get("items", []):
                html += f"""
            <div class="mb-4">
                <h3 class="text-xl font-semibold">{item.get('degree', '')}</h3>
                <p class="text-gray-600">{item.get('school', '')} | {item.get('year', '')}</p>
            </div>
"""
            html += """
        </section>
"""
        elif section_type == "skills":
            html += f"""
        <section class="mb-6">
            <h2 class="text-2xl font-bold primary-color mb-4">{content.get('title', 'Skills')}</h2>
            <div class="flex flex-wrap gap-2">
"""
            for skill in content.get("items", []):
                html += f"""
                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">{skill}</span>
"""
            html += """
            </div>
        </section>
"""
    
    html += """
    </div>
</body>
</html>
"""
    return html


def _generate_nextjs_index(ui_json: Dict[str, Any]) -> str:
    """Generate Next.js index page component."""
    return f"""
import React from 'react';

export default function Resume() {{
  const uiData = {json.dumps(ui_json, indent=4)};
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto bg-white shadow-lg p-8">
        <h1>Resume Preview</h1>
        <pre>{{JSON.stringify(uiData, null, 2)}}</pre>
      </div>
    </div>
  );
}}
"""


def _create_zip_bundle(source_dir: str, zip_path: str):
    """Create zip bundle from source directory."""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)


