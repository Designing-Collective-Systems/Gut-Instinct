import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const projectRoot = process.env.PWD || process.cwd();
const scriptPath  = path.join(projectRoot, 'public', 'standalone-viz', 'iMSMS_emperor.py');
const outputHtml  = path.join(projectRoot, 'public', 'standalone-viz', 'visualization.html');
const scriptCwd   = path.dirname(scriptPath);

// venv paths
const venvBin    = path.join(projectRoot, '.venv', process.platform === 'win32' ? 'Scripts' : 'bin');
const venvPython = path.join(venvBin, process.platform === 'win32' ? 'python.exe' : 'python');

function pickPython() {
  const candidates = [
    process.env.PYTHON,     // allow override
    venvPython,             // prefer project venv
    '/usr/bin/python3',
    'python3',
    'python',
  ].filter(Boolean);

  for (const p of candidates) {
    try { execFileSync(p, ['--version'], { stdio: 'ignore' }); return p; } catch {}
  }
  return null;
}

Meteor.methods({
  runPythonVisualization({ variable1, variable2 }) {
    check(variable1, String);
    console.log(variable1)
    console.log(variable2)
    check(variable2, String);
    this.unblock();

    if (!fs.existsSync(scriptPath)) {
      throw new Meteor.Error('script-not-found', `No script at ${scriptPath}`);
    }

    const python = pickPython();
    if (!python) throw new Meteor.Error('python-not-found', 'No Python interpreter found');

    // Ensure the spawned process sees the venv first
    const env = {
      ...process.env,
      VIRTUAL_ENV: fs.existsSync(venvBin) ? path.resolve(projectRoot, '.venv') : process.env.VIRTUAL_ENV,
      PATH: `${venvBin}:${process.env.PATH || ''}`,
      // If you ever vendor deps with --target server/python_deps, uncomment:
      // PYTHONPATH: path.join(projectRoot, 'server', 'python_deps'),
    };

    try {
      // small probe so logs show which interpreter is used
      const probe = execFileSync(python, ['-c', 'import sys; print(sys.executable)'], { env, encoding: 'utf8' });
      console.log('[viz] using python:', probe.trim());

      const stdout = execFileSync(python, [scriptPath, variable1, variable2], {
        cwd: scriptCwd,
        env,
        encoding: 'utf8',
        timeout: 120000,
      });
      console.log('[viz] python stdout:', stdout);

      // ADD THE DEBUG CODE RIGHT HERE ↓↓↓
      console.log('[debug] Checking file after Python execution:');
      console.log('[debug] File exists:', fs.existsSync(outputHtml));
      if (fs.existsSync(outputHtml)) {
        const stats = fs.statSync(outputHtml);
        console.log('[debug] File modified:', stats.mtime);
        console.log('[debug] File size:', stats.size);
        // Read first few characters to verify content
        const content = fs.readFileSync(outputHtml, 'utf8').slice(0, 200);
        console.log('[debug] File content preview:', content);
      }
      console.log('[debug] Full file path:', outputHtml);
      console.log('[debug] Current working directory:', process.cwd());
      // Add this right after your existing debug code
      if (fs.existsSync(outputHtml)) {
        const content = fs.readFileSync(outputHtml, 'utf8');
        // Look for your timestamp in the HTML content
        const timestampMatch = content.match(/Generated on: ([^<]+)/);
        if (timestampMatch) {
          console.log('[debug] HTML timestamp in file:', timestampMatch[1]);
        }
        // Look for the variable being used in the HTML
        const variableMatch = content.match(/variable1.*?(\w+)/i);
        if (variableMatch) {
          console.log('[debug] Variable found in HTML:', variableMatch[1]);
        }
      }
      // END DEBUG CODE ↑↑↑
      
    } catch (e) {
      const msg = (e.stderr?.toString?.() || e.message || String(e)).slice(0, 4000);
      console.error('[viz] python failed:', msg);
      throw new Meteor.Error('exec-failed', msg);
    }

    if (!fs.existsSync(outputHtml)) {
      throw new Meteor.Error('output-missing', `Expected output at ${outputHtml} not found`);
    }

    return { success: true, outputPath: '/standalone-viz/visualization.html' };
  },
});
