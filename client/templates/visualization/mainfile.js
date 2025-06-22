// mainfile.js converted to Flow Router

import { Template } from 'meteor/templating';
import { FlowRouter } from 'meteor/kadira:flow-router';
import { BlazeLayout } from 'meteor/kadira:blaze-layout';

// No configuration is needed for this basic setup in Flow Router.

// Define the root route
FlowRouter.route('/', {
    name: 'home', // It's good practice to name your routes
    action() {
        // Instead of this.render, Flow Router uses BlazeLayout
        BlazeLayout.render('gaVisualization');
    }
});

// Define the new route for the visualization page
FlowRouter.route('/galileo/visualization', {
    name: 'visualization',
    action() {
        BlazeLayout.render('gaVisualization');
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