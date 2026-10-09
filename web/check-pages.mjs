import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));
const pages = ["index.html", "compare.html", "mechanism.html", "scoring.html"];
const problems = [];

for (const page of pages) {
  const html = fs.readFileSync(path.join(root, page), "utf8");
  const links = [...html.matchAll(/href="([^"]+)"/g)].map((match) => match[1]);
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);

  for (const destination of pages) {
    if (!links.includes(destination)) problems.push(`${page}: no navigation link to ${destination}`);
  }
  for (const href of links) {
    if (!/^(?:https?:|mailto:|tel:|#)/i.test(href) && href.endsWith(".html") && !fs.existsSync(path.join(root, href))) {
      problems.push(`${page}: link target is missing (${href})`);
    }
    if (href === "#" || href === "") problems.push(`${page}: dead/empty link`);
  }
  for (const [, target] of html.matchAll(/aria-controls="([^"]+)"/g)) {
    if (!ids.includes(target)) problems.push(`${page}: aria-controls target is missing (#${target})`);
  }
  for (const [, id] of html.matchAll(/\bid="([^"]+)"/g)) {
    if (ids.filter((candidate) => candidate === id).length > 1) problems.push(`${page}: duplicate id (${id})`);
  }
  if (!html.includes('<main id="main"')) problems.push(`${page}: main landmark is missing`);
  if (!html.includes('href="styles.css"') || !html.includes('src="app.js"')) {
    problems.push(`${page}: shared CSS or interaction script is not linked`);
  }
}

if (problems.length) {
  console.error(problems.join("\n"));
  process.exitCode = 1;
} else {
  console.log(`Checked ${pages.length} pages: navigation targets, local links, ARIA targets, IDs, landmarks, and shared assets are valid.`);
}
