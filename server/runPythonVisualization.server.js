import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { execFileSync, spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { WebApp } from 'meteor/webapp';

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
// UPDATED: Dynamic route handler that generates HTML on-demand
WebApp.connectHandlers.use('/standalone-viz/visualization.html', (req, res, next) => {
  try {
    // Get variables from query params or use defaults
    const var1 = req.query.var1 || 'Age';
    const var2 = req.query.var2 || 'default';
    
    console.log(`[route] Generating visualization for: ${var1}, ${var2}`);
    
    if (!fs.existsSync(scriptPath)) {
      console.error(`[route] Script not found: ${scriptPath}`);
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end(`Script not found: ${scriptPath}`);
      return;
    }

    const python = pickPython();
    if (!python) {
      console.error('[route] No Python interpreter found');
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('No Python interpreter found');
      return;
    }

    // Ensure the spawned process sees the venv first
    const env = {
      ...process.env,
      VIRTUAL_ENV: fs.existsSync(venvBin) ? path.resolve(projectRoot, '.venv') : process.env.VIRTUAL_ENV,
      PATH: `${venvBin}:${process.env.PATH || ''}`,
    };

    console.log('[route] Using python:', python);
    console.log('[route] Script path:', scriptPath);
    console.log('[route] Variables:', { var1, var2 });
    
    // Spawn Python process to capture stdout
    const pythonProcess = spawn(python, [scriptPath, var1, var2], {
      cwd: scriptCwd,
      env: env
    });
    
    let htmlOutput = '';
    let errorOutput = '';
    
    // Capture stdout (the HTML)
    pythonProcess.stdout.on('data', (data) => {
      htmlOutput += data.toString();
    });
    
    // Capture stderr (for debugging - your debug messages)
    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.log('[route] Python debug:', data.toString());
    });
    
    // When Python script finishes
    pythonProcess.on('close', (code) => {
      console.log(`[route] Python process finished with code: ${code}`);
      console.log(`[route] HTML output length: ${htmlOutput.length}`);
      console.log(`[route] Error output length: ${errorOutput.length}`);
      
      if (code === 0 && htmlOutput.trim()) {
        // Set no-cache headers to prevent caching issues
        res.writeHead(200, {
          'Content-Type': 'text/html',
          'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
          'Pragma': 'no-cache',
          'Expires': '0'
        });
        res.end(htmlOutput);
        console.log('[route] Successfully served HTML from Python stdout');
      } else {
        console.error(`[route] Python script error (code ${code}):`, errorOutput);
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end(`Error generating visualization. Code: ${code}\nError: ${errorOutput}`);
      }
    });
    
    pythonProcess.on('error', (err) => {
      console.error(`[route] Failed to start Python process:`, err);
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Failed to generate visualization: ' + err.message);
    });
    
    // Set timeout to prevent hanging requests
    const timeout = setTimeout(() => {
      console.error('[route] Python process timeout');
      pythonProcess.kill();
      if (!res.headersSent) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Visualization generation timeout');
      }
    }, 120000); // 2 minutes
    
    pythonProcess.on('close', () => {
      clearTimeout(timeout);
    });
    
  } catch (error) {
    console.error('[route] Error in visualization route:', error);
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end('Internal server error: ' + error.message);
  }
});

// KEEP YOUR EXISTING METHOD FOR BACKWARD COMPATIBILITY (but it can be simplified)
Meteor.methods({
  runPythonVisualization({ variable1, variable2 }) {
    check(variable1, String);
    console.log(variable1)
    console.log(variable2)
    check(variable2, String);
    this.unblock();

    // Since we're now using the dynamic route, we can simplify this method
    // Just return success immediately - the route will handle the actual generation
    return { 
      success: true, 
      outputPath: `/standalone-viz/visualization.html?var1=${encodeURIComponent(variable1)}&var2=${encodeURIComponent(variable2)}&t=${Date.now()}` 
    };
  },
});