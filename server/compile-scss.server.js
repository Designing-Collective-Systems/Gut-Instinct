// ‼️  NO top‑level import that the browser would choke on
const { Meteor } = require('meteor/meteor');   // ← CommonJS, browser never sees it

if (Meteor.isServer) {
  // use CommonJS requires so the code never reaches the client bundle
  const sass = require('sass');  // ← changed from 'node-sass' to 'sass'
  const fs   = require('fs');
  const path = require('path');

const PROJECT_ROOT = '.';   // ← adjust if you move the repo

// input ↔ output pairs
const inputFilePath1  = path.join(PROJECT_ROOT, 'client/styles/main.scss');
const outputFilePath1 = path.join(PROJECT_ROOT, 'public/css/main.css');

const inputFilePath2  = path.join(PROJECT_ROOT, 'client/styles/ga-main.scss');
const outputFilePath2 = path.join(PROJECT_ROOT, 'public/css/ga-main.css');

// Compile first file
try {
  const result1 = sass.compile(inputFilePath1, {
    style: 'compressed'
  });
  fs.writeFileSync(outputFilePath1, result1.css);
  console.log('main.scss compiled successfully!');
} catch (error) {
  console.error('Sass compilation error for main.scss:', error);
}

// Compile second file
try {
  const result2 = sass.compile(inputFilePath2, {
    style: 'compressed'
  });
  fs.writeFileSync(outputFilePath2, result2.css);
  console.log('ga-main.scss compiled successfully!');
} catch (error) {
  console.error('Sass compilation error for ga-main.scss:', error);
}
}