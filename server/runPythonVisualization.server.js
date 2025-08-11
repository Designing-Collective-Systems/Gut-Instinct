import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

// Resolve paths without import.meta
// In dev, PWD points to your project root. Fallback to cwd.
const projectRoot = process.env.PWD || process.cwd();
const scriptPath  = path.join(projectRoot, 'public', 'standalone-viz', 'iMSMS_emperor.py');
const outputHtml  = path.join(projectRoot, 'public', 'standalone-viz', 'visualization.html');
const scriptCwd   = path.dirname(scriptPath);

console.log('[viz] server file loaded');
console.log('[viz] scriptPath =', scriptPath);

Meteor.methods({
  runPythonVisualization({ variable1, variable2 }) {
    check(variable1, String);
    check(variable2, String);
    this.unblock();

    console.log('[viz] start', { variable1, variable2 });

    if (!fs.existsSync(scriptPath)) {
      throw new Meteor.Error('script-not-found', `No script at ${scriptPath}`);
    }

    // Pick a python binary that exists
    const candidates = ['/usr/bin/python3', 'python3', 'python'];
    const python = candidates.find(p => {
      try { execFileSync(p, ['--version'], { stdio: 'ignore' }); return true; } catch { return false; }
    });
    if (!python) throw new Meteor.Error('python-not-found', 'No Python interpreter found on server');

    try {
      const stdout = execFileSync(python, [scriptPath, variable1, variable2], {
        cwd: scriptCwd,
        encoding: 'utf8',
        timeout: 120000,
      });
      console.log('[viz] python stdout:', stdout);
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
