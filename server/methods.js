import { Meteor } from 'meteor/meteor';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

Meteor.methods({
  'runPythonVisualization'(variable1, variable2) {
    // Validate inputs
    if (!variable1 || !variable2) {
      throw new Meteor.Error('invalid-params', 'Both variables are required');
    }

    console.log(`Running Python visualization with variables: ${variable1}, ${variable2}`);

    // Since Meteor runs from a build directory, we need to find the source project
    // Get the actual project root by going up from the current Meteor build directory
    const currentDir = process.cwd();
    console.log('Current Meteor working directory:', currentDir);
    
    // Navigate back to the actual project directory
    // From: /path/to/project/.meteor/local/build/programs/server
    // To:   /path/to/project
    const projectRoot = path.resolve(currentDir, '../../../../../');
    console.log('Calculated project root:', projectRoot);
    
    const pythonScriptPath = path.join(projectRoot, 'public', 'standalone-viz', 'iMSMS_emperor.py');
    const outputDir = path.join(projectRoot, 'public', 'standalone-viz');
    
    console.log('Looking for Python script at:', pythonScriptPath);
    console.log('Output directory:', outputDir);

    // Check if Python script exists
    if (!fs.existsSync(pythonScriptPath)) {
      // If the calculated path doesn't work, try to find the project directory
      console.log('Calculated path failed. Trying to find project directory...');
      
      // Look for common project indicators
      let searchDir = currentDir;
      let maxAttempts = 10;
      let found = false;
      
      for (let i = 0; i < maxAttempts; i++) {
        const testProjectDir = path.resolve(searchDir, '../'.repeat(i));
        const testScriptPath = path.join(testProjectDir, 'public', 'standalone-viz', 'iMSMS_emperor.py');
        
        console.log(`Attempt ${i + 1}: Testing ${testScriptPath}`);
        
        if (fs.existsSync(testScriptPath)) {
          pythonScriptPath = testScriptPath;
          outputDir = path.dirname(testScriptPath);
          found = true;
          console.log('Found script at:', pythonScriptPath);
          break;
        }
      }
      
      if (!found) {
        throw new Meteor.Error('script-not-found', `Python script not found. Last tried: ${pythonScriptPath}`);
      }
    }

    // Execute Python script with variables as arguments
    // Try different Python commands since 'python' might not be available
    const pythonCommands = ['python3', 'python', '/usr/bin/python3', '/usr/bin/python'];
    
    let pythonCmd = null;
    
    // Test which Python command is available
    for (const cmd of pythonCommands) {
      try {
        const { execSync } = require('child_process');
        execSync(`${cmd} --version`, { stdio: 'ignore' });
        pythonCmd = cmd;
        console.log(`Found Python command: ${cmd}`);
        break;
      } catch (error) {
        console.log(`${cmd} not available`);
      }
    }
    
    if (!pythonCmd) {
      throw new Meteor.Error('python-not-found', 'No Python interpreter found. Please install Python.');
    }
    
    const command = `${pythonCmd} "${pythonScriptPath}" "${variable1}" "${variable2}"`;
    
    try {
      const { execSync } = require('child_process');
      console.log('here')
      console.log(`Executing command: ${command}`);
      console.log(`Working directory: ${outputDir}`);
      
      const output = execSync(command, { 
        cwd: outputDir,
        encoding: 'utf8',
        timeout: 120000 // 2 minute timeout
      });
      
      console.log('Python script output:', output);
      
      // Check if the output file was created
      const expectedOutputPath = path.join(outputDir, 'visualization.html');
      if (fs.existsSync(expectedOutputPath)) {
        return {
          success: true,
          message: 'Visualization generated successfully',
          outputPath: '/standalone-viz/visualization.html'
        };
      } else {
        throw new Meteor.Error('output-not-found', 'Python script ran but output file was not created');
      }
      
    } catch (error) {
      console.error('Error executing Python script:', error);
      throw new Meteor.Error('execution-failed', `Python script execution failed: ${error.message}`);
    }
  }
});