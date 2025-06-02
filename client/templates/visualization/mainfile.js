// Update the existing _.js file to include the new route for visualization
import { Template } from 'meteor/templating';
import { Router } from 'meteor/iron:router';

// Configure Iron Router
Router.configure({
    noRoutesTemplate: null
});

// Define routes
Router.route('/', function() {
    this.render('gaVisualization');
});

// Add new route for the visualization page
Router.route('/galileo/visualization', function() {
    this.render('gaVisualization');
});

// Events for gaQuestions template
Template.gaQuestions.onCreated(function() {
    // Initialize any necessary variables
});

// Template.gaQuestions.events({
//     'click #seeViz': function(event) {
//         event.preventDefault();
//         // Instead of redirecting to external URL, use Router to navigate to our new route
//         Router.go('/galileo/visualization');
//     }
// });