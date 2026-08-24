"""Generate the GitHub Pages deployment workflow for the Nihongo N5 site.

Writes `.github/workflows/deploy-pages.yml` which publishes the static
site located at `work/20260824-nihongo-n5/site` to GitHub Pages.
"""
import os

WORKFLOW = r"""name: Deploy Nihongo N5 to GitHub Pages

on:
  push:
    branches: [main]
    paths:
      - 'work/20260824-nihongo-n5/site/**'
      - '.github/workflows/deploy-pages.yml'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages-nihongo-n5
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: work/20260824-nihongo-n5/site
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                   ".github", "workflows", "deploy-pages.yml")


def main() -> None:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(WORKFLOW)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
