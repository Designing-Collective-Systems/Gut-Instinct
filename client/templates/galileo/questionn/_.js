import './_.html'; // This imports the associated HTML template for gaQuestions
import { Template } from 'meteor/templating';
import { FlowRouter } from 'meteor/kadira:flow-router';

Template.gaQuestions.onCreated(function () {
  // Initialization logic (if needed)
});

Template.gaQuestions.events({
  'click #seeViz': function (event) {
    event.preventDefault();
    console.log('Button clicked!');
    
    // Read input values
    const variable1 = document.getElementById('variable1').value.trim();
    const variable2 = document.getElementById('variable2').value.trim();
    
    console.log('Variable 1:', variable1);
    console.log('Variable 2:', variable2);
    
    // Check for both inputs
    if (!variable1 || !variable2) {
      alert('Please enter both variables before proceeding.');
      return;
    }
    
    console.log('Calling Meteor method: runPythonVisualization');
    
    Meteor.call('runPythonVisualizationn', { variable1, variable2 }, (error, result) => {
      if (error) {
        console.error('Error running visualization:', error);
        alert('Error generating visualization: ' + error.reason);
      } else {
        console.log('Python script setup successful:', result);
        
        // Navigate directly to the dynamic route with parameters
        // This will trigger the WebApp route handler that generates HTML on-demand
        const timestamp = Date.now();
        const dynamicUrl = `/standalone-viz/visualizationn.html?var1=${encodeURIComponent(variable1)}&var2=${encodeURIComponent(variable2)}&t=${timestamp}`;
        
        console.log('Navigating to dynamic visualization URL:', dynamicUrl);
        
        // Navigate after short delay to allow for any cleanup
        setTimeout(() => {
          window.location.href = dynamicUrl;
        }, 500);
      }
    });
  }
});