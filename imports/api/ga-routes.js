// Modern Meteor 3.2 Galileo Routes with FlowRouter and Blaze 3.0.2
import { FlowRouter } from 'meteor/kadira:flow-router';
import { Blaze } from 'meteor/blaze';
import { Template } from 'meteor/templating';
import { Meteor } from 'meteor/meteor';
import { Session } from 'meteor/session';
import { $ } from 'meteor/jquery';

import {
    ParticipationStatus,
    ErrorMessage
} from "./ga-models/constants";
import { Bookmarks } from './models';
import { UserMetrics } from '../api/models.js';

// Helper function to redirect
export function redirect(newPath) {
    FlowRouter.go(newPath);
}

// Store current view reference for cleanup
let currentView = null;

// Helper function to check if template exists
function templateExists(templateName) {
    return Template[templateName] && typeof Template[templateName] !== 'undefined';
}

// Helper function to wait for a template to be available.
// NOTE: This is a safety net. The root cause of templates not being found is usually
// a missing `import './template.html';` statement in your client-side code.
function waitForTemplate(templateName, maxAttempts = 10) {
    return new Promise(resolve => {
        let attempts = 0;
        const checkTemplate = () => {
            attempts++;
            if (templateExists(templateName)) {
                resolve(true);
            } else if (attempts >= maxAttempts) {
                console.warn(`Template ${templateName} not found after ${maxAttempts} attempts`);
                resolve(false);
            } else {
                setTimeout(checkTemplate, 100);
            }
        };
        checkTemplate();
    });
}

// Helper function to render template with data
async function renderTemplate(templateName, data = {}) {
    // Clean up previous view if it exists
    if (currentView) {
        try {
            Blaze.remove(currentView);
        } catch (e) {
            console.warn('Could not remove previous view:', e);
        }
        currentView = null;
    }

    // Clear the body
    $('body').empty();

    // Wait for template to be available before rendering
    const templateAvailable = await waitForTemplate(templateName);

    if (!templateAvailable) {
        console.error('Template not found after waiting:', templateName);
        $('body').html(`
            <div class="error-container" style="padding: 20px; text-align: center;">
                <h2>Template Not Found</h2>
                <p>The template "${templateName}" could not be found.</p>
                <p>Please check your template imports and definitions.</p>
                <details style="margin: 20px 0;">
                    <summary>Available Templates:</summary>
                    <pre style="text-align: left; background: #f5f5f5; padding: 10px; margin: 10px 0;">
${Object.keys(Template).filter(key => !key.startsWith('_')).sort().join('\n')}
                    </pre>
                </details>
                <button onclick="history.back()" style="padding: 10px 20px; margin: 10px;">Go Back</button>
                <button onclick="window.location.href='/galileo/home'" style="padding: 10px 20px; margin: 10px;">Go Home</button>
            </div>
        `);
        return;
    }

    // Render new template and store the view
    // Use Meteor.defer to ensure DOM is ready before Blaze rendering
    Meteor.defer(() => {
        try {
            if (Object.keys(data).length > 0) {
                currentView = Blaze.renderWithData(Template[templateName], data, document.body);
            } else {
                currentView = Blaze.render(Template[templateName], document.body);
            }
        } catch (innerError) {
            console.error('Error rendering template after defer:', templateName, innerError);

            // Fallback for imageModal remains as a safety net
            if (innerError.message && innerError.message.includes('imageModal')) {
                console.log('ImageModal dependency issue detected. Attempting to create fallback...');
                if (!Template.imageModal) {
                    Template.imageModal = new Template('Template.imageModal', function() {
                        return HTML.DIV({ class: 'modal fade', id: 'imageModal' }, [
                            HTML.DIV({ class: 'modal-dialog' }, [
                                HTML.DIV({ class: 'modal-content' }, [
                                    HTML.DIV({ class: 'modal-body' }, [
                                        HTML.IMG({ class: 'img-responsive', src: '', alt: 'Image' })
                                    ])
                                ])
                            ])
                        ]);
                    });
                }
                // Try rendering again with the fallback
                setTimeout(() => {
                    try {
                        currentView = Blaze.renderWithData(Template[templateName], data, document.body);
                    } catch (retryError) {
                        console.error('Error on retry:', retryError);
                        showTemplateError(templateName, retryError);
                    }
                }, 100);
            } else {
                showTemplateError(templateName, innerError);
            }
        }
    });
}

// Helper function to show template errors
function showTemplateError(templateName, error) {
    $('body').html(`
        <div class="error-container" style="padding: 20px; text-align: center;">
            <h2>Template Rendering Error</h2>
            <p>Error rendering template "${templateName}": ${error.message}</p>
            <details style="margin: 20px 0;">
                <summary>Error Details:</summary>
                <pre style="text-align: left; background: #f5f5f5; padding: 10px; margin: 10px 0; border: 1px solid #ddd;">
${error.stack || error.message}
                </pre>
            </details>
            <button onclick="history.back()" style="padding: 10px 20px; margin: 10px;">Go Back</button>
            <button onclick="window.location.href='/galileo/home'" style="padding: 10px 20px; margin: 10px;">Go Home</button>
        </div>
    `);
}

// Helper function to logout user
async function logoutUser() {
    try {
        await Meteor.logoutAsync();
        sessionStorage.clear();
        localStorage.clear();
        FlowRouter.go('/galileo/home');
    } catch (err) {
        console.log('Error logging out:', err);
    }
}

// Helper function to check if user can go to browse
function canGoToBrowse(user) {
    if (user) {
        if (!user.profile?.consent_agreed) {
            FlowRouter.go('/galileo/consent');
            return false;
        }
        if (!user.profile?.toured?.username_page) {
            FlowRouter.go('/galileo/username');
            return false;
        }
        return true;
    }
    return false;
}

// Helper function to convert to camelCase
function toCamelCase(str) {
    return str.split("_").map(word => word.charAt(0).toUpperCase() + word.substring(1)).join("");
}

// Helper function to attempt profile update
async function attemptUpdateProfile() {
    if (!Meteor.userId()) {
        return;
    }
    try {
        const hasProfile = await Meteor.callAsync('galileo.profile.hasProfile');
        if (!hasProfile) {
            await Meteor.callAsync('galileo.profile.updateProfile');
        }
    } catch (err) {
        console.error('Failed to update profile:', err);
    }
}


// Root route
FlowRouter.route('/', {
    action() {
        FlowRouter.go('/galileo');
    }
});

// Legacy routes
FlowRouter.route('/gaExperimentDesign', { action() { renderTemplate('gaExperimentDesign'); } });
FlowRouter.route('/gutboard_slider_addq', { action() { renderTemplate('gutboard_slider_addq'); } });
FlowRouter.route('/tutorial', { action() { renderTemplate('tutorial'); } });
FlowRouter.route('/welcome', { action() { renderTemplate('welcome'); } });
FlowRouter.route('/gutboard', { action() { renderTemplate('gutboard'); } });
FlowRouter.route('/test', { action() { renderTemplate('test'); } });
FlowRouter.route('/guide', { action() { renderTemplate('guide_question_welcome'); } });
FlowRouter.route('/problems', { action() { renderTemplate('problems'); } });
FlowRouter.route('/articles', { action() { renderTemplate('articles'); } });
FlowRouter.route('/bookmark', { action() { renderTemplate('bookmark'); } });
FlowRouter.route('/landing', { action() { renderTemplate('landing'); } });
FlowRouter.route('/trial', { action() { renderTemplate('trial', { type: "pre" }); } });
FlowRouter.route('/survey', { action() { renderTemplate('post_survey', { type: "post" }); } });

// Authentication routes
FlowRouter.route('/login-admin', {
    action() {
        if (!Meteor.userId()) {
            renderTemplate('login');
        } else {
            FlowRouter.go('/consent');
        }
    }
});

// Main Galileo route
FlowRouter.route('/galileo', {
    action: async function() {
        const user = await Meteor.userAsync();
        if (user) {
            try {
                const relativeExperiments = await Meteor.callAsync('galileo.profile.getRelativeExperiments', user);
                if (relativeExperiments?.length > 0) {
                    FlowRouter.go('/galileo/me/dashboard');
                } else {
                    FlowRouter.go('/galileo/browse');
                }
            } catch (err) {
                console.error("Error getting relative experiments:", err);
                FlowRouter.go('/galileo/browse');
            }
        } else {
            FlowRouter.go('/galileo/browse');
        }
    }
});

// Galileo signup
FlowRouter.route('/galileo/signup', {
    action() {
        if (!Meteor.userId()) {
            renderTemplate('signup');
        } else {
            FlowRouter.go('/galileo/consent');
        }
    }
});

// Galileo consent
FlowRouter.route('/galileo/consent', {
    action: async function() {
        const user = await Meteor.userAsync();
        if (!user) {
            FlowRouter.go('/galileo/signup');
            return;
        }

        if (!user.profile?.consent_agreed) {
            renderTemplate('consent');
            return;
        }

        if (!user.profile?.toured?.username_page) {
            FlowRouter.go('/galileo/username');
            return;
        }

        const loginRedirectUrl = localStorage.getItem("loginRedirectUrl");
        if (loginRedirectUrl) {
            try {
                const mendelCode = await Meteor.callAsync('galileo.profile.getMendel');
                localStorage.setItem("mendelcode_ga", mendelCode);
                localStorage.removeItem('loginRedirectUrl');
                FlowRouter.go(loginRedirectUrl);
            } catch (err) {
                console.error("Error getting Mendel code:", err);
                FlowRouter.go('/galileo/browse');
            }
            return;
        }

        try {
            const relativeExperiments = await Meteor.callAsync('galileo.profile.getRelativeExperiments', user._id);
            if (!localStorage.getItem("mendelcode_ga") || localStorage.getItem("mendelcode_ga") === "undefined") {
                const mendelCode = await Meteor.callAsync('galileo.profile.getMendel');
                localStorage.setItem("mendelcode_ga", mendelCode);
            }

            if (relativeExperiments?.length > 0) {
                FlowRouter.go('/galileo/me/dashboard');
            } else {
                FlowRouter.go('/galileo/browse');
            }
        } catch (err) {
            console.error("Error in consent routing logic:", err);
            FlowRouter.go('/galileo/browse');
        }
    }
});

// Demo routes
FlowRouter.route('/galileo/createdemo', {
    action: async function(params, queryParams) {
        const user = await Meteor.userAsync();
        if (user) {
            if (!user.profile?.consent_agreed) {
                FlowRouter.go('/galileo/consent');
            } else if (!user.profile?.toured?.username_page) {
                FlowRouter.go('/galileo/username');
            } else {
                renderTemplate('gaCreateDemo', queryParams.expid ? { expId: queryParams.expid } : {});
            }
        } else {
            renderTemplate('gaCreateDemo');
        }
    }
});

FlowRouter.route('/galileo/addcriteria', {
    action(params, queryParams) {
        if (queryParams.expid) {
            renderTemplate('gaCriteriaDemo', { expId: queryParams.expid });
        }
    }
});

FlowRouter.route('/m', {
    action() {
        renderTemplate('gaEducationDemo');
    }
});

FlowRouter.route('/galileo/createedu', {
    action: async function(params, queryParams) {
        const user = await Meteor.userAsync();
        if (user) {
            if (!user.profile?.consent_agreed) {
                FlowRouter.go('/galileo/consent');
            } else if (!user.profile?.toured?.username_page) {
                FlowRouter.go('/galileo/username');
            } else if (queryParams.expid) {
                renderTemplate('gaEducationDemo', { expId: queryParams.expid });
            }
        }
    }
});

// Username route
FlowRouter.route('/galileo/username', {
    action() {
        renderTemplate('username', { isGalileo: true });
    }
});

// Logout route
FlowRouter.route('/galileo/logout', {
    action: async function() {
        try {
            await Meteor.callAsync('galileo.profile.setMendel', localStorage.getItem('mendelcode_ga'));
        } catch (err) {
            console.error("Failed to set Mendel code on logout:", err);
        } finally {
            logoutUser();
        }
    }
});

// Basic Galileo routes
FlowRouter.route('/galileo/console', { action() { renderTemplate('gaConsole'); } });
FlowRouter.route('/galileo/home', { action() { renderTemplate('gaHome'); } });
FlowRouter.route('/galileo/questions', { action() { renderTemplate('gaQuestions'); } });
FlowRouter.route('/galileo/visualization', { action() { renderTemplate('emperorVisualization'); } });
FlowRouter.route('/galileo/entrance', { action() { renderTemplate('gaEntrance'); } });
FlowRouter.route('/galileo/landing', { action() { renderTemplate('gaLanding'); } });

// Blog routes
const blogRoutes = [
    { path: '/galileo/blog/why-exp', redirect: '/galileo/blog/tutorial' },
    { path: '/galileo/blog/why-exp-openhumans', template: 'gabWhyExpOH' },
    { path: '/galileo/blog/why-exp-lyme', template: 'gabWhyExpLyme' },
    { path: '/galileo/blog/why-exp-beer', template: 'gabWhyExpBeer' },
    { path: '/galileo/blog/why-exp-nerdnite', template: 'gabWhyExpNerdNite' },
    { path: '/galileo/blog/why-exp-probiotics', template: 'gabWhyProbiotics' },
    { path: '/galileo/blog/why-exp-spice', template: 'gabWhyExpSpice' },
    { path: '/galileo/blog/why-exp-circadian', template: 'gabWhyExpCircadian' },
    { path: '/galileo/blog/why-exp-kombucha', template: 'gabWhyExpKombucha' },
    { path: '/galileo/blog/why-exp-t1d', template: 'gabWhyExpT1D' },
    { path: '/galileo/blog/why-exp-kefir', template: 'gabWhyExpKefir' },
    { path: '/galileo/blog/why-exp-agp', template: 'gabWhyExpAGP' },
    { path: '/galileo/blog/why-exp-gut-check', template: 'gabWhyExpGutCheck' },
    { path: '/galileo/blog/why-exp-soylent', template: 'gabWhyExpSoylent' },
    { path: '/galileo/blog/why-exp-diet', template: 'gabWhyExpDiet' },
    { path: '/galileo/blog/tutorial', template: 'gabTutorial' }
];

blogRoutes.forEach(route => {
    FlowRouter.route(route.path, {
        action() {
            if (route.redirect) {
                FlowRouter.go(route.redirect);
            } else {
                renderTemplate(route.template);
            }
        }
    });
});

// Tour route
FlowRouter.route('/galileo/tour', {
    action: async function() {
        try {
            const progress = await Meteor.callAsync("galileo.tour.getProgress");
            switch (progress) {
                case "create":
                    const expId = await Meteor.callAsync("galileo.tour.getDesignedExperimentId");
                    if (expId) {
                        Session.set("currentExperimentId", expId);
                        FlowRouter.go(`/galileo/create?expid=${expId}`);
                    } else {
                        const intuitionId = await Meteor.callAsync("galileo.tour.getSelectedIntuitionId");
                        if (intuitionId) {
                            const intuition = await Meteor.callAsync("galileo.intuition.getIntuitionById", intuitionId);
                            FlowRouter.go(`/galileo/create?int=${encodeURI(intuition.intuition)}`);
                        } else {
                            FlowRouter.go("/galileo/create");
                        }
                    }
                    break;
                case "feedback":
                case "pilot":
                    FlowRouter.go("/galileo/browse");
                    break;
                default:
                    FlowRouter.go(`/galileo/${progress}`);
                    break;
            }
        } catch (err) {
            console.error("Error getting tour progress:", err);
            FlowRouter.go('/galileo/browse');
        }
    }
});

// Tutorial routes
FlowRouter.route('/galileo/intro', {
    action() {
        if (Meteor.userId()) {
            Meteor.call("galileo.tour.startTour", (e) => e && console.error(e)); // Fire and forget
            Meteor.call("galileo.tour.finishIntro", (e) => e && console.error(e)); // Fire and forget
        }
        renderTemplate('gaIntro');
    }
});

FlowRouter.route('/galileo/pretest', {
    action: async function() {
        try {
            const can = await Meteor.callAsync("galileo.tour.canPretest");
            if (can) {
                renderTemplate('gaPreTest');
            } else {
                FlowRouter.go("/galileo/intro");
            }
        } catch (err) {
            console.error(err);
            FlowRouter.go("/galileo/intro");
        }
    }
});

FlowRouter.route('/galileo/intuition', { action: async function() { await renderTemplate('gaIntuition'); } });
FlowRouter.route('/galileo/intuition_board', { action: async function() { await renderTemplate('gaIntuitionBoard'); } });


// Create route
FlowRouter.route('/galileo/create', {
    action: async function(params, queryParams) {
        try {
            const can = await Meteor.callAsync("galileo.tour.canCreate");
            if (can) {
                let data = {};
                if (queryParams.int) data.intuition = queryParams.int;
                else if (queryParams.intid) data.intuitionId = queryParams.intid;
                else if (queryParams.expid) data.expId = queryParams.expid;
                renderTemplate('gaCreateMain', data);
            } else {
                FlowRouter.go("/galileo/intuition_board");
            }
        } catch (err) {
            console.error(err);
            FlowRouter.go("/galileo/intuition_board");
        }
    }
});

// Feedback route
FlowRouter.route('/galileo/feedback', {
    action: async function(params, queryParams) {
        const expId = queryParams.exp_id;
        const user = await Meteor.userAsync();

        if (!user) {
            renderTemplate('gaExperimentFeedback', { id: expId, guest_mode: true });
            return;
        }

        try {
            const isFeedbacking = await Meteor.callAsync("galileo.feedback.isFeedbacking", expId, 'galileo/feedback routes');
            const isCreator = await Meteor.callAsync("galileo.experiments.isCreator", expId);

            if (isFeedbacking || isCreator || user.profile?.is_admin) {
                renderTemplate('gaExperimentFeedback', { id: expId });
            } else {
                const canFeedback = await Meteor.callAsync("galileo.feedback.canFeedback", expId);
                if (canFeedback) {
                    renderTemplate('gaFeedbackConsent', { id: expId });
                } else {
                    console.error("Sorry, you cannot give feedback to this experiment");
                    setTimeout(() => FlowRouter.go("/galileo/browse"), 5000);
                }
            }
        } catch (err) {
            console.error(err.reason || err.message);
            setTimeout(() => FlowRouter.go("/galileo/browse"), 5000);
        }
    }
});

// Pilot feedback route
FlowRouter.route('/galileo/pilotFeedback', {
    action: async function(params, queryParams) {
        const { exp_id: expId, pilot_id: pilotId } = queryParams;

        try {
            if (expId && pilotId) {
                const canSee = await Meteor.callAsync("galileo.pilot.canUserSeePilotFeedback", expId, pilotId);
                if (canSee) {
                    renderTemplate('gaExperimentFeedback', { id: expId, pilotId: pilotId });
                } else {
                    throw new Error("Sorry, you cannot view this pilot feedback.");
                }
            } else if (expId) {
                const userPilotId = await Meteor.callAsync("galileo.pilot.hasPiloted", expId);
                if (userPilotId) {
                    renderTemplate('gaExperimentFeedback', { id: expId, pilotId: userPilotId });
                } else {
                    throw new Error("Sorry, you cannot give pilot feedback to this experiment.");
                }
            }
        } catch (err) {
            console.error("Error: " + (err.reason || err.message));
            setTimeout(() => history.back(), 3000);
        }
    }
});


// Pilot route
FlowRouter.route('/galileo/pilot', {
    action: async function(params, queryParams) {
        const expId = queryParams.exp_id;
        try {
            await Meteor.callAsync("galileo.pilot.canPilot", expId);
            renderTemplate('gaPilot', { id: expId });
        } catch (err) {
            console.error("Error: " + (err.reason || err.message));
        }
    }
});

// Run route
FlowRouter.route('/galileo/run', {
    action(params, queryParams) {
        renderTemplate('gaRun', { id: queryParams.exp_id });
    }
});

// Share review route
FlowRouter.route('/galileo/share/review', {
    action(params, queryParams) {
        const expId = queryParams.exp_id;
        if (!Meteor.userId()) {
            renderTemplate('gaFeedbackConsent', { id: expId, guest_mode: true });
        } else {
            FlowRouter.go(`/galileo/feedback?exp_id=${expId}`);
        }
    }
});

// Browse route
FlowRouter.route('/galileo/browse', {
    action: async function(params, queryParams) {
        const user = await Meteor.userAsync();
        if (!user) {
            FlowRouter.go("/galileo/home");
            return;
        }

        if (user.profile) {
            if (queryParams.mendelcode?.length > 0) {
                renderTemplate('gaExperimentBoard');
                localStorage.setItem("mendelcode_ga", queryParams.mendelcode);
            } else if (canGoToBrowse(user)) {
                renderTemplate('gaExperimentBoard');
            }
        }
    }
});

// Browse flag route
FlowRouter.route('/galileo/browse_flag', {
    action() {
        renderTemplate('gaExperimentBoard', { flag: true });
    }
});

// Experiment route
FlowRouter.route('/galileo/experiment', {
    action(params, queryParams) {
        if (queryParams.exp_id) {
            renderTemplate('gaExperimentBoard', { id: queryParams.exp_id });
        }
    }
});

// Criteria route
FlowRouter.route('/galileo/criteria', {
    action(params, queryParams) {
        if (queryParams.exp_id) {
            renderTemplate('gaCheckCriteria', { id: queryParams.exp_id });
        }
    }
});

// Join route
FlowRouter.route('/galileo/join', {
    action: async function(params, queryParams) {
        const expId = queryParams.exp_id;
        if (!expId) return;

        try {
            const canParticipate = await Meteor.callAsync("galileo.run.canParticipate", expId);
            if (canParticipate) {
                FlowRouter.go(`/galileo/join/criteria?exp_id=${expId}`);
            }
        } catch (err) {
            if (err.error === ErrorMessage.IS_REVIEWER_CANNOT_JOIN) {
                FlowRouter.go(`/galileo/join/failed?exp_id=${expId}`);
                return;
            }

            try {
                const status = await Meteor.callAsync("galileo.run.getParticipantStatus", expId);
                switch (status) {
                    case ParticipationStatus.PASSED_CRITERIA:
                    case ParticipationStatus.PREPARING:
                        FlowRouter.go(`/galileo/me/experiment/my_participation?exp_id=${expId}`);
                        break;
                    case ParticipationStatus.FAILED_CRITERIA:
                        FlowRouter.go(`/galileo/join/failed?exp_id=${expId}`);
                        break;
                    case ParticipationStatus.FINISHED:
                        FlowRouter.go(`/galileo/join/failedEnded?exp_id=${expId}`);
                        break;
                    default:
                        FlowRouter.go('/galileo/browse/');
                        break;
                }
            } catch (statusErr) {
                console.error("Could not get participant status", statusErr);
                FlowRouter.go('/galileo/browse/');
            }
        }
    }
});

// Share join route
FlowRouter.route('/galileo/share/join', {
    action(params, queryParams) {
        if (queryParams.exp_id) {
            FlowRouter.go(`/galileo/join/criteria?exp_id=${queryParams.exp_id}`);
        }
    }
});

// Join routes
FlowRouter.route('/galileo/join/consent', { action(p, q) { if (q.exp_id) renderTemplate('gaJoinConsent', { id: q.exp_id }); } });
FlowRouter.route('/galileo/join/criteria', { action(p, q) { if (q.exp_id) renderTemplate('gaJoinCriteria', { id: q.exp_id }); } });
FlowRouter.route('/galileo/join/openhumansauth', { action(p, q) { if (q.exp_id) renderTemplate('gaOhAuth', { id: q.exp_id }); } });
FlowRouter.route('/galileo/join/failed', { action(p, q) { if (q.exp_id) renderTemplate('gaJoinFailed', { id: q.exp_id }); } });
FlowRouter.route('/galileo/join/failedEnded', { action(p, q) { if (q.expid) renderTemplate('gaJoinFailedEnded', { id: q.expid }); } });

// Join passed route
FlowRouter.route('/galileo/join/passed', {
    action(params, queryParams) {
        if (queryParams.exp_id) {
            FlowRouter.go(`/galileo/join/openhumansauth?exp_id=${queryParams.exp_id}`);
        }
    }
});


// Me routes
FlowRouter.route('/galileo/me', { action() { FlowRouter.go('/galileo/me/dashboard'); } });

FlowRouter.route('/galileo/me/dashboard', {
    action(params, queryParams) {
        if (queryParams.user_id && queryParams.exp_id) {
            $(document).ready(() => {
                const isMobile = window.matchMedia("only screen and (max-width: 760px)").matches;
                if (isMobile) {
                    renderTemplate('gaMeDataSheet', { exp_id: queryParams.exp_id, user_id: queryParams.user_id });
                } else {
                    attemptUpdateProfile().finally(() => FlowRouter.go('/galileo/me/dashboard'));
                }
            });
        } else {
            renderTemplate('gaMeDashboard');
        }
    }
});


// Additional Me routes
const meRoutes = [
    { path: '/galileo/me/notification', template: 'gaMeNotification' },
    { path: '/galileo/me/password', template: 'gaMePassword' },
    { path: '/galileo/me/profile', template: 'gaMeProfile' },
    { path: '/galileo/me/intuitions', template: 'gaMeIntuitions' },
    { path: '/galileo/me/unfinished_experiments', template: 'gaMeUnfinishedExperiments' },
    { path: '/galileo/me/created_experiments', template: 'gaMeCreatedExperiments' },
    { path: '/galileo/me/reviewing_experiments', template: 'gaMeReviewingExperiments' },
    { path: '/galileo/me/pilot_experiments', template: 'gaMePilotExperiments' },
    { path: '/galileo/me/participating_experiments', template: 'gaMeParticipatingExperiments' }
];
meRoutes.forEach(route => { FlowRouter.route(route.path, { action() { renderTemplate(route.template); } }); });


// Me experiment route
FlowRouter.route('/galileo/me/experiment', {
    action: async function(params, queryParams) {
        const expId = queryParams.exp_id;
        try {
            const isFailed = await Meteor.callAsync('galileo.run.isFailedCriteria', expId);
            if (isFailed) {
                FlowRouter.go(`/galileo/join/failed?exp_id=${expId}`);
            } else {
                FlowRouter.go(`/galileo/me/experiment/info?exp_id=${expId}`);
            }
        } catch (err) {
            console.error(err);
            FlowRouter.go(`/galileo/browse`);
        }
    }
});

// Me experiment with section route
FlowRouter.route('/galileo/me/experiment/:section', {
    action: async function(params, queryParams) {
        const { exp_id: expId } = queryParams;
        const { section } = params;

        try {
            const exp = await Meteor.callAsync("galileo.experiments.getExperiment", expId);
            const creatorID = exp.user_id;

            if (section === "design") {
                const user = await Meteor.userAsync();
                const canDesign = await Meteor.callAsync("galileo.experiments.isCreator", expId);
                if (canDesign || user?.profile?.is_admin) {
                    renderTemplate('gaExperimentFeedback', { id: expId, expCreatorId: creatorID, guest_mode: false });
                } else {
                    FlowRouter.go(`/galileo/feedback?exp_id=${expId}`);
                }
            } else {
                renderTemplate('gaMeExperiment', { id: expId, section: section });
            }
        } catch (err) {
            console.error(err.reason || err.message);
            setTimeout(() => FlowRouter.go("/galileo/browse"), 5000);
        }
    }
});

// Me experiment info route
FlowRouter.route('/galileo/me/experiment/info', {
    action(params, queryParams) {
        renderTemplate('gaMeExperiment', { id: queryParams.exp_id, section: 'info' });
    }
});

// Me experiment my participation route
FlowRouter.route('/galileo/me/experiment/my_participation', {
    action(params, queryParams) {
        renderTemplate('gaMeExperiment', { id: queryParams.exp_id, section: 'my_participation' });
    }
});


// FAQ route
FlowRouter.route('/gafaqs', { action() { renderTemplate('gaFaqs'); } });

// Error route
FlowRouter.route('/galileo/error', {
    action(params, queryParams) {
        renderTemplate('gaError', { code: queryParams.code, msg: queryParams.msg });
    }
});

// Global route guards and triggers
FlowRouter.triggers.enter([
    function(context) {
        console.log('Entering route:', context.path);
    }
]);

FlowRouter.triggers.exit([
    function() {
        if (currentView) {
            try {
                Blaze.remove(currentView);
                currentView = null;
            } catch (e) {
                console.warn('Could not remove view on route exit:', e);
            }
        }
    }
]);

// Not found route
FlowRouter.notFound = {
    action() {
        renderTemplate('gaError', { code: '404', msg: 'Page not found' });
    }
};

// Export helper functions for use in other files
export {
    canGoToBrowse,
    attemptUpdateProfile,
    toCamelCase,
    renderTemplate
};