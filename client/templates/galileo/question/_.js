import './_.html';
import { Template } from 'meteor/templating';
import { Router } from 'meteor/iron:router';

// Configure Iron Router
Router.configure({
    noRoutesTemplate: null
});

// Define routes
Router.route('/', function() {
    this.render('gaQuestions');
});

Router.route('/galileo/questions', function() {
    this.render('gaQuestions');
});

Template.gaQuestions.onCreated(function() {
    // Initialize any necessary variables
});

Template.gaQuestions.events({
    'click #seeViz': function(event) {
        event.preventDefault();
        console.log('Button clicked!'); // Add this to verify the click is working
        
        // Get the values from both input fields
        const variable1 = document.getElementById('variable1').value;
        const variable2 = document.getElementById('variable2').value;
        
        console.log('Variable 1:', variable1);
        console.log('Variable 2:', variable2);
        
        // Check if both variables are entered
        if (!variable1 || !variable2) {
            alert('Please enter both variables before proceeding.');
            return;
        }
        
        console.log('About to call Meteor method...'); // Add this debug line
        
        // Call Meteor method to process variables and run Python script
        Meteor.call('runPythonVisualization', variable1, variable2, function(error, result) {
            if (error) {
                console.error('Error running visualization:', error);
                alert('Error generating visualization: ' + error.reason);
            } else {
                console.log('Python script executed successfully:', result);
                
                // Small delay to ensure file is fully written and server is ready
                setTimeout(() => {
                    window.location.href = '/galileo/visualization';
                }, 5000); // Half second delay
            }
        });
    }
});