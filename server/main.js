// server/main.js
const path = require('path');
const fs   = require('fs');

function abs(p) {
  // always resolves to <projectRoot>/script/source/<file>
  return path.resolve(process.cwd(), 'script', 'source', p);
}

function loadDatabase () {
  // synchronous reset
  SurveyQuestions.rawCollection().drop().catch(() => {});
  Boards.rawCollection().drop().catch(() => {});
  Examples.rawCollection().drop().catch(() => {});

  const survey   = JSON.parse(fs.readFileSync(abs('survey_questions.json'), 'utf8'));
  const boards   = JSON.parse(fs.readFileSync(abs('galileo_boards.json'),   'utf8'));
  const examples = JSON.parse(fs.readFileSync(abs('galileo_examples.json'), 'utf8'));

  survey.forEach(doc   => SurveyQuestions.insert(doc));
  boards.forEach(doc   => Boards.insert(doc));
  examples.forEach(doc => Examples.insert(doc));
}
