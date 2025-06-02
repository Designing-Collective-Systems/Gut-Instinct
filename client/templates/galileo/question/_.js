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
        // Redirect to Google.com when the link is clicked
        window.location.href = 'http://127.0.0.1:5500/iMSMS_emperor_host_static_html/modifiedEmperor.html';
    }
});