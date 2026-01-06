import os
import json
from typing import Dict, Any

TEMPLATE_DIR = "templates"
BUILD_DIR = "builds"


class BuildEngine:
    """
    Builds a static website from generated semantic content.
    """

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        job = state["job"]
        content = state["generated_content"]
        template = state.get("template", "default")

        output_dir = os.path.join(BUILD_DIR, job["job_id"])
        os.makedirs(output_dir, exist_ok=True)

        html = self._render_html(content)

        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)

        # Save metadata
        with open(os.path.join(output_dir, "content.json"), "w") as f:
            json.dump(content, f, indent=2)

        state["build"] = {
            "output_dir": output_dir,
            "entrypoint": index_path
        }

        return state

    def _render_html(self, content: Dict[str, Any]) -> str:
        hero = content["hero"]
        bio = content["bio"]
        projects = content.get("projects", [])

        project_html = "".join(
            f"<li><strong>{p['title']}</strong>: {p['description']}</li>"
            for p in projects
        )

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>{hero['name']} | Portfolio</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body>
  <header>
    <h1>{hero['name']}</h1>
    <p>{hero['tagline']}</p>
  </header>

  <section>
    <h2>About</h2>
    <p>{bio}</p>
  </section>

  <section>
    <h2>Projects</h2>
    <ul>{project_html}</ul>
  </section>
</body>
</html>
<<<<<<< HEAD
"""
=======
"""
>>>>>>> 1e6abe464a5baebe118a48d62818195d91f563e5
