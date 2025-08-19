import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const projectRoot = process.env.PWD || process.cwd();
const scriptPath  = path.join(projectRoot, 'public', 'standalone-viz', 'iMSMS_emperorn.py');
const outputHtml  = path.join(projectRoot, 'public', 'standalone-viz', 'visualizationn.html');
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
  runPythonVisualizationn({ variable1, variable2 }) {
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
    } catch (e) {
      const msg = (e.stderr?.toString?.() || e.message || String(e)).slice(0, 4000);
      console.error('[viz] python failed:', msg);
      throw new Meteor.Error('exec-failed', msg);
    }

    if (!fs.existsSync(outputHtml)) {
      throw new Meteor.Error('output-missing', `Expected output at ${outputHtml} not found`);
    }

    return { success: true, outputPath: '/standalone-viz/visualizationn.html' };
  },
});
