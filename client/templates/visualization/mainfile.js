// mainfile.js with Flow Router and Blaze 3.0.2

import { Template } from 'meteor/templating';
import { Blaze } from 'meteor/blaze';
import { FlowRouter } from 'meteor/kadira:flow-router';

// No configuration is needed for this basic setup in Flow Router.

// Define the root route
FlowRouter.route('/', {
    name: 'home', // It's good practice to name your routes
    action() {
        // Use Blaze.render instead of BlazeLayout
        Blaze.render(Template.gaVisualization, document.body);
    }
});

// Define the new route for the visualization page
FlowRouter.route('/galileo/visualization', {
    name: 'visualization',
    action() {
        Blaze.render(Template.gaVisualization, document.body);
    }
});

// Events for gaQuestions template (this part remains the same)
Template.gaQuestions.onCreated(function() {
    // Initialize any necessary variables
});

// The event helper, updated for Flow Router
Template.gaQuestions.events({
    'click #seeViz': function(event) {
        event.preventDefault();
        // Use FlowRouter.go() to navigate. Using the route name is recommended.
        FlowRouter.go('visualization');
    }
});