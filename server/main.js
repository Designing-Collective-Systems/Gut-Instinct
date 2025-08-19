// server/main.js
import path from 'path';
import fs from 'fs/promises'; // Use promises-based fs API
import { Meteor } from 'meteor/meteor';

// Import your collections
import { SurveyQuestions } from '../imports/api/server/surveyQuestions.js';
import { Boards } from '../imports/api/ga-models/boards.js';
import { Examples } from '../imports/api/ga-models/examples.js';

import './runPythonVisualization.server.js';
import './runPythonVisualizationn.server.js';




function abs(p) {
  // always resolves to <projectRoot>/script/source/<file>
  return path.resolve(process.cwd(), 'script', 'source', p);
}

async function loadDatabase() {
  try {
    console.log('Starting database initialization...');

    // Use modern async/await with proper error handling
    await Promise.allSettled([
      SurveyQuestions.rawCollection().deleteMany({}),
      Boards.rawCollection().deleteMany({}),
      Examples.rawCollection().deleteMany({})
    ]);

    console.log('Collections cleared successfully');

    // Load JSON files asynchronously
    const [surveyData, boardsData, examplesData] = await Promise.all([
      fs.readFile(abs('survey_questions.json'), 'utf8'),
      fs.readFile(abs('galileo_boards.json'), 'utf8'),
      fs.readFile(abs('galileo_examples.json'), 'utf8')
    ]);

    // Parse JSON data
    const survey = JSON.parse(surveyData);
    const boards = JSON.parse(boardsData);
    const examples = JSON.parse(examplesData);

    console.log(`Loaded ${survey.length} survey questions, ${boards.length} boards, ${examples.length} examples`);

    // Use modern insertMany for better performance
    const insertPromises = [];

    if (survey.length > 0) {
      insertPromises.push(SurveyQuestions.rawCollection().insertMany(survey));
    }
    
    if (boards.length > 0) {
      insertPromises.push(Boards.rawCollection().insertMany(boards));
    }
    
    if (examples.length > 0) {
      insertPromises.push(Examples.rawCollection().insertMany(examples));
    }

    await Promise.all(insertPromises);

    console.log('Database initialization completed successfully');

  } catch (error) {
    console.error('Error during database initialization:', error);
    throw error;
  }
}

// Alternative approach using Meteor's async methods (if available in your collections)
async function loadDatabaseMeteorAsync() {
  try {
    console.log('Starting database initialization with Meteor async methods...');

    // Use Meteor's async methods if available
    await Promise.allSettled([
      SurveyQuestions.removeAsync({}),
      Boards.removeAsync({}),
      Examples.removeAsync({})
    ]);

    console.log('Collections cleared successfully');

    // Load JSON files
    const [surveyData, boardsData, examplesData] = await Promise.all([
      fs.readFile(abs('survey_questions.json'), 'utf8'),
      fs.readFile(abs('galileo_boards.json'), 'utf8'),
      fs.readFile(abs('galileo_examples.json'), 'utf8')
    ]);

    const survey = JSON.parse(surveyData);
    const boards = JSON.parse(boardsData);
    const examples = JSON.parse(examplesData);

    // Insert documents using Meteor async methods
    const insertPromises = [];

    for (const doc of survey) {
      insertPromises.push(SurveyQuestions.insertAsync(doc));
    }

    for (const doc of boards) {
      insertPromises.push(Boards.insertAsync(doc));
    }

    for (const doc of examples) {
      insertPromises.push(Examples.insertAsync(doc));
    }

    await Promise.all(insertPromises);

    console.log('Database initialization completed successfully');

  } catch (error) {
    console.error('Error during database initialization:', error);
    throw error;
  }
}

// Optimized version for large datasets
async function loadDatabaseOptimized() {
  try {
    console.log('Starting optimized database initialization...');

    // Clear collections with better error handling
    const clearOperations = [
      { collection: SurveyQuestions, name: 'SurveyQuestions' },
      { collection: Boards, name: 'Boards' },
      { collection: Examples, name: 'Examples' }
    ];

    for (const { collection, name } of clearOperations) {
      try {
        await collection.rawCollection().deleteMany({});
        console.log(`Cleared ${name} collection`);
      } catch (error) {
        console.warn(`Failed to clear ${name} collection:`, error.message);
      }
    }

    // Load and parse files with error handling
    const fileOperations = [
      { path: abs('survey_questions.json'), collection: SurveyQuestions, name: 'survey questions' },
      { path: abs('galileo_boards.json'), collection: Boards, name: 'boards' },
      { path: abs('galileo_examples.json'), collection: Examples, name: 'examples' }
    ];

    for (const { path: filePath, collection, name } of fileOperations) {
      try {
        // Check if file exists
        await fs.access(filePath);
        
        const data = await fs.readFile(filePath, 'utf8');
        const documents = JSON.parse(data);

        if (documents.length > 0) {
          // Use ordered: false for better performance with large datasets
          await collection.rawCollection().insertMany(documents, { ordered: false });
          console.log(`Inserted ${documents.length} ${name}`);
        } else {
          console.log(`No ${name} to insert`);
        }
      } catch (error) {
        console.error(`Failed to load ${name} from ${filePath}:`, error.message);
        // Continue with other files even if one fails
      }
    }

    console.log('Database initialization completed');

  } catch (error) {
    console.error('Error during database initialization:', error);
    throw error;
  }
}

// Meteor startup with proper error handling
Meteor.startup(async () => {
  console.log('Server starting up...');

  try {
    // Choose one of the loading methods based on your needs:
    
    // Method 1: Direct MongoDB operations (fastest)
    await loadDatabase();
    
    // Method 2: Meteor async methods (if you need Meteor hooks)
    // await loadDatabaseMeteorAsync();
    
    // Method 3: Optimized for large datasets
    // await loadDatabaseOptimized();

  } catch (error) {
    console.error('Failed to initialize database:', error);
    // Optionally exit the process if database initialization is critical
    // process.exit(1);
  }

  console.log('Server startup completed');
});

// Alternative: Load database only in development
if (Meteor.isDevelopment) {
  Meteor.startup(async () => {
    console.log('Development mode: Initializing database...');
    
    try {
      // Check if collections are empty before loading
      const [surveyCount, boardsCount, examplesCount] = await Promise.all([
        SurveyQuestions.find().countAsync(),
        Boards.find().countAsync(),
        Examples.find().countAsync()
      ]);

      if (surveyCount === 0 || boardsCount === 0 || examplesCount === 0) {
        console.log('Collections are empty, loading initial data...');
        await loadDatabase();
      } else {
        console.log('Collections already populated, skipping initialization');
      }
    } catch (error) {
      console.error('Error checking/loading database:', error);
    }
  });
}

// Export functions for testing or manual execution
export { loadDatabase, loadDatabaseMeteorAsync, loadDatabaseOptimized };