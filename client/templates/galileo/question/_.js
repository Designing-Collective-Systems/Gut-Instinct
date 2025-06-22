import './_.html'; // This imports the associated HTML template for gaQuestions
import { Template } from 'meteor/templating';
import { FlowRouter } from 'meteor/kadira:flow-router'; // Import FlowRouter

// --- REMOVED ---
// Router.configure({
//     noRoutesTemplate: null
// });
// Router.route('/', function() { ... });
// Router.route('/galileo/questions', function() { ... });
// --- END REMOVED ---

Template.gaQuestions.onCreated(function() {
    // Initialize any necessary variables
});

Template.gaQuestions.events({
    'click #seeViz': function(event) {
        event.preventDefault();
        console.log('Button clicked!');

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

        console.log('About to call Meteor method...');

        // Call Meteor method to process variables and run Python script
        Meteor.call('runPythonVisualization', variable1, variable2, function(error, result) {
            if (error) {
                console.error('Error running visualization:', error);
                alert('Error generating visualization: ' + error.reason);
            } else {
                console.log('Python script executed successfully:', result);

                // Use FlowRouter.go for internal routing
                setTimeout(() => {
                    FlowRouter.go('/galileo/visualization');
                }, 500); // Changed to 500ms, adjust if necessary
            }
        });
    }
});