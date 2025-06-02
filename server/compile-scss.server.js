// ‼️  NO top‑level import that the browser would choke on
const { Meteor } = require('meteor/meteor');   // ← CommonJS, browser never sees it

if (Meteor.isServer) {
  // use CommonJS requires so the code never reaches the client bundle
  const sass  = require('node-sass');
  const fs    = require('fs');
  const path  = require('path');

const PROJECT_ROOT = '.';   // ← adjust if you move the repo

// input ↔ output pairs
const inputFilePath1  = path.join(PROJECT_ROOT, 'client/styles/main.scss');
const outputFilePath1 = path.join(PROJECT_ROOT, 'public/css/main.css');

const inputFilePath2  = path.join(PROJECT_ROOT, 'client/styles/ga-main.scss');
const outputFilePath2 = path.join(PROJECT_ROOT, 'public/css/ga-main.css');

sass.render({
  file: inputFilePath1,
  outFile: outputFilePath1,
  outputStyle: 'compressed'
}, (error, result) => {
  if (error) {
    console.error('Sass compilation error:', error);
    return;
  }
  fs.writeFileSync(outputFilePath1, result.css);
  console.log('Sass compiled successfully!');
});

sass.render({
  file: inputFilePath2,
  outFile: outputFilePath2,
  outputStyle: 'compressed'
}, (error, result) => {
  if (error) {
    console.error('Sass compilation error:', error);
    return;
  }
  fs.writeFileSync(outputFilePath2, result.css);
  console.log('Sass compiled successfully!');
});
}
