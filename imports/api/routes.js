import { FlowRouter } from 'meteor/kadira:flow-router';
import { BlazeLayout } from 'meteor/kadira:blaze-layout';

// Import your collections (models.js)
import {
    UserMetrics,
    UserEmail,
    UserTestResponse
} from './models.js';

// Assuming you still need this for GA tracking if it doesn't rely on Iron Router specific hooks
import './ga-routes.js';

// Set the root element for BlazeLayout to render into
BlazeLayout.setRoot('body');

// --- Global Before Action (Authentication Guard) ---
// This handles the logic that was in your Router.onBeforeAction

const checkLoggedIn = function(context, redirect) {
    // Show a loading wheel while checking login status
    BlazeLayout.render('layout', { main: 'loading_wheel' });

    // Use a reactive computation to re-run when Meteor.userAsync() changes
    this.autorun(() => {
        if (!Meteor.userAsync() && !Meteor.loggingIn()) {
            // Your original Iron Router logic for unauthenticated users
            // This part had commented out logic and a redirect to /galileo/home
            redirect('/galileo/home'); // Consistent with your uncommented redirect

            // Stop this autorun to prevent unnecessary re-runs
            this.stop();
        } else if (Meteor.userAsync()) {
            // User is logged in, proceed to the next trigger/route action
            this.next();
            this.stop(); // Stop this autorun once user is logged in
        }
        // If Meteor.loggingIn() is true, just keep showing loading_wheel and wait
    });
};

// Define routes that *do not* require authentication,
// or handle authentication within their own specific `action` if they allow guest access.
const publicRoutesExclusions = [
    'landing', 'login-process', 'login-error', 'login-admin', 'logout', 'intro',
    'login-admin1', 'signup', 'auth_openhumans', 'galileo.home', 'galileo.signup',
    'galileo.landing', 'galileo.browse', 'galileo.experiment', 'reset-password',
    "galileo.share.review", "galileo.share.review.guest", "galileo.experiment.feedback",
    "galileo.join.consent", "galileo.blog.why-exp", "galileo.blog.why-exp-openhumans",
    "galileo.blog.why-exp-lyme", "galileo.blog.why-exp-kefir", 'galileo.blog.why-exp-T1D',
    'galileo.blog.why-exp-kombucha', "galileo.blog.tutorial", "galileo.blog.why-exp-agp",
    "galileo.me.datasheet", "galileo.blog.why-exp-gut-check", 'galileo.blog.why-exp-soylent',
    'galileo.blog.why-exp-diet', 'galileo.join', 'galileo.join.criteria', 'galileo.share.join',
    "galileo.blog.why-exp-beer", "galileo.blog.why-exp-spice", "galileo.blog.why-exp-circadian",
    "galileo.blog.why-exp-nerdnite", "galileo.blog.why-exp-probiotics"
];


// Main application group, applies the authentication check
const appRoutes = FlowRouter.group({
    triggersEnter: [checkLoggedIn],
    except: publicRoutesExclusions // Apply `checkLoggedIn` to all routes EXCEPT these
});


// --- Helper for Profile-based Redirects ---
// This logic is repeated in many of your Iron Router routes.
// We can make a helper function for clarity.
const checkUserProfileAndRedirect = function(redirect) {
    const user = Meteor.userAsync();
    if (!user) {
        // This case should ideally be handled by the global `checkLoggedIn` trigger
        // but included for robustness if a route is somehow accessed directly without it.
        redirect('/galileo/home');
        return true; // Indicates a redirect happened
    }
    const profile = user.profile;

    if (!profile.consent_agagreed) {
        redirect('/consent');
        return true;
    }
    if (!profile.toured?.username_page) { // Using optional chaining for safety
        redirect('/username');
        return true;
    }
    if (!profile.took_pretest) {
        redirect('/trial');
        return true;
    }
    if (!profile.intro_completed) {
        const docentProgress = localStorage.getItem("docentProgress");
        if (docentProgress && (docentProgress == 25 || docentProgress == 50)) {
            redirect('/t/introduction');
            // Materialize.toast calls are UI specific and best placed in template `onRendered` or `onCreated` if dependent on user state
            return true;
        }
        if (docentProgress && docentProgress == 85) {
            redirect('gutboard_slider_addq');
            // Materialize.toast calls
            return true;
        }
        redirect('/guide');
        // Materialize.toast calls
        return true;
    }
    return false; // No redirect needed, proceed
};

// Function for toast messages (Materialize Toast)
// This should ideally be moved to a client-side utility file
const showToast = (message, duration = 4000) => {
    if (typeof Materialize !== 'undefined' && Materialize.toast) {
        Materialize.toast(message, duration, 'toast');
    } else {
        console.warn("Materialize.toast is not available. Message:", message);
    }
};

// --- ROUTES ---

// Root Redirect (similar to your Iron Router '/' route)
FlowRouter.route('/', {
    name: 'root',
    action: function() {
        // This route is primarily for initial redirection
        FlowRouter.go('/galileo');
    }
});

// The actual /galileo route (assuming this is where the app effectively starts)
// Adjust this if '/galileo' maps to a specific template
FlowRouter.route('/galileo', {
    name: 'galileo.home_redirect', // Or whatever makes sense
    action: function() {
        // This mirrors your commented out Iron Router logic for '/'
        if (Meteor.userAsync()) {
            // Check specific profile conditions and redirect
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return; // Redirect happened, stop
            }
            // If no redirects from profile check, then handle the main logic
            if (Meteor.userAsync().profile.condition == 7) {
                FlowRouter.go('/topics');
            } else {
                FlowRouter.go('gutboard'); // Or 'gutboard_slider' based on original code
            }
        } else {
            console.log("Meteor-user0");
            BlazeLayout.render('layout', { main: 'home' }); // Render 'home' for guests
        }
    }
});


appRoutes.route('/login-admin', {
    name: 'login-admin',
    action: function() {
        if (!Meteor.userAsync()) {
            BlazeLayout.render('layout', { main: 'login' });
        } else {
            FlowRouter.go('consent'); // Corrected from this.redirect
        }
    }
});

appRoutes.route('/signup', {
    name: 'signup',
    action: function() {
        if (!Meteor.userAsync()) {
            BlazeLayout.render('layout', { main: 'signup' });
        } else {
            BlazeLayout.render('layout', { main: 'loading_wheel' }); // Render loading wheel
            FlowRouter.go('/galileo/consent');
        }
    }
});

appRoutes.route('/login-admin1', {
    name: 'login-admin1',
    action: function() {
        if (!Meteor.userAsync()) {
            BlazeLayout.render('layout', { main: 'new_login' });
        } else {
            FlowRouter.go('consent');
        }
    }
});

appRoutes.route('/consent', {
    name: 'consent',
    action: function() {
        if (!Meteor.userAsync()?.profile?.consent_agreed) { // Optional chaining for safety
            Meteor.call("galileo.profile.updateProfile");
            BlazeLayout.render('layout', { main: 'consent' });
        } else {
            FlowRouter.go('/intro');
        }
    }
});

appRoutes.route('/tutorial', {
    name: 'tutorial',
    action: function() {
        BlazeLayout.render('layout', { main: 'tutorial' });
    }
});

appRoutes.route('/gutboard', {
    name: 'gutboard',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            // if (Meteor.userAsync()?.profile?.questions?.length == 1 && Meteor.userAsync()?.profile?.intro_completed) {
            //     FlowRouter.go('/addq');
            //     showToast('You need to add one other question before accessing the entire Gut Instinct content', 4000);
            //     return;
            // }
            if (Meteor.userAsync()?.profile?.condition != 7) {
                BlazeLayout.render('layout', {
                    main: 'gutboard_slider',
                    data: { mendelcode: "AmericanGutProject" }
                });
            }
        } catch (e) {
            console.error("Error in /gutboard route:", e);
        }
    },
    waitOn: function() { // Add subscriptions relevant to this route here
        // Example: Meteor.subscribe('someGutboardData');
        return [];
    }
});

appRoutes.route('/gutboard/:mendelcode', {
    name: 'gutboard_with_code',
    action: function(params) {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            // if (Meteor.userAsync()?.profile?.questions?.length == 1 && Meteor.userAsync()?.profile?.intro_completed) {
            //     FlowRouter.go('/addq');
            //     showToast('You need to add one other question before accessing the entire Gut Instinct content', 4000);
            //     return;
            // }
            if (Meteor.userAsync()?.profile?.condition != 7) {
                BlazeLayout.render('layout', {
                    main: 'gutboard_slider',
                    data: { mendelcode: params.mendelcode }
                });
            }
        } catch (e) {
            console.error("Error in /gutboard/:mendelcode route:", e);
        }
    },
    waitOn: function() {
        // Example: Meteor.subscribe('someGutboardData', this.params.mendelcode);
        return [];
    }
});

appRoutes.route('/gutboard/:mendelcode/search', {
    name: 'gutboard_search',
    action: function(params, queryParams) {
        BlazeLayout.render('layout', {
            main: 'gutboard_search',
            data: {
                mendelcode: params.mendelcode,
                searchQuery: queryParams.q
            }
        });
    }
});

appRoutes.route('/addq', {
    name: 'addq',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }

            const userProfile = Meteor.userAsync()?.profile;
            if (userProfile && userProfile.intro_completed && !userProfile.guide_completed &&
                (userProfile.condition == 10 || userProfile.condition == 11)) {
                FlowRouter.go('/guide');
                showToast('Before asking more questions, just complete this quick guide about asking useful questions', 5000);
                return;
            }

            if (userProfile && userProfile.condition != 7) {
                BlazeLayout.render('layout', { main: 'gutboard_slider_addq' });
            }
        } catch (e) {
            console.error("Error in /addq route:", e);
        }
    }
});

appRoutes.route('/gutboard_slider_addq', {
    name: 'gutboard_slider_addq',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }

            const userProfile = Meteor.userAsync()?.profile;
            if (userProfile && userProfile.intro_completed && !userProfile.guide_completed) {
                FlowRouter.go('/guide');
                showToast('Before asking more questions, just complete this quick guide about asking useful questions', 5000);
                return;
            }

            if (userProfile && userProfile.condition != 7) {
                BlazeLayout.render('layout', { main: 'gutboard_slider_addq' });
            }
        } catch (e) {
            console.error("Error in /gutboard_slider_addq route:", e);
        }
    }
});

appRoutes.route('/gutboard_old', {
    name: 'gutboard_old',
    action: function() {
        const user = Meteor.userAsync();
        const condition = user?.profile?.condition;

        if (condition == 1) {
            FlowRouter.go('problems');
            return;
        }
        BlazeLayout.render('layout', { main: 'gutboard' });
    }
});

appRoutes.route('/gutboard_slider', {
    name: 'gutboard_slider',
    action: function() {
        const user = Meteor.userAsync();
        if (!user) {
            console.log("Meteor-userg");
            FlowRouter.go('/galileo/home'); // Redirect if no user (should be caught by global trigger but good for robustness)
            return;
        }

        if (checkUserProfileAndRedirect(FlowRouter.go)) {
            return;
        }

        const condition = user.profile.condition;
        if (condition == 1 || condition == 8) {
            BlazeLayout.render('layout', { main: 'gutboard_slider' });
        } else {
            if (!user.profile.guide_completed) {
                FlowRouter.go('/guide');
            } else {
                BlazeLayout.render('layout', { main: 'gutboard_slider' });
            }
        }
    }
});

appRoutes.route('/problems', {
    name: 'problems',
    action: function() {
        const condition = Meteor.userAsync()?.profile?.condition;
        if (condition != 1) {
            FlowRouter.go('gutboard');
            return;
        }
        BlazeLayout.render('layout', { main: 'problems' });
    }
});

appRoutes.route('/articles', {
    name: 'articles',
    action: function() {
        const condition = Meteor.userAsync()?.profile?.condition;
        if (condition != 2) {
            FlowRouter.go('gutboard');
            return;
        }
        BlazeLayout.render('layout', { main: 'articles' });
    }
});

appRoutes.route('/bookmark', {
    name: 'bookmark',
    action: function() {
        const condition = Meteor.userAsync()?.profile?.condition;
        if (false && condition != 1) { // This condition is always false, mirroring original
            FlowRouter.go('gutboard');
            return;
        }
        BlazeLayout.render('layout', { main: 'bookmark' });
    }
});

appRoutes.route('/welcome', {
    name: 'welcome',
    action: function() {
        // Using setTimeout here to mimic original async behavior, though
        // FlowRouter's `waitOn` and `action` are synchronous after subs ready.
        // If this relies on `Meteor.userAsync` being ready, use `waitOn`.
        this.autorun(() => {
            const user = Meteor.userAsync();
            if (!user) {
                console.log("Meteor-userw");
                // The global checkLoggedIn trigger should handle this if user is not logged in.
                return;
            }

            const username = user.username;
            const TestResult = UserTestResponse.findOne({ "username": username });

            if (TestResult == undefined) {
                FlowRouter.go('/username');
            } else {
                FlowRouter.go('/gutboard');
                // FlowRouter.go('/t/introduction'); // If this is the desired path
            }
            this.stop(); // Stop autorun after the check
        });
        BlazeLayout.render('layout', { main: 'loading_wheel' }); // Render loading while checking
    }
});

appRoutes.route('/welcome_uncheck', {
    name: 'welcome_uncheck',
    action: function() {
        const currentUser = Meteor.userAsync();
        if (!currentUser) {
            FlowRouter.go('/galileo/home'); // Or login page
            return;
        }
        const currentUsername = currentUser.username;
        const fetchResult = UserEmail.findOne({ "username": currentUsername });

        if (fetchResult == undefined) {
            UserEmail.insert({
                username: currentUsername,
                agree: 0,
                email: "",
                agid: ""
            });
        }
        BlazeLayout.render('layout', { main: 'welcome' });
    }
});

appRoutes.route('/welcome_step1', {
    name: 'welcome_step1',
    action: function() {
        FlowRouter.go('welcome_step2');
    }
});

appRoutes.route('/username', {
    name: 'username',
    action: function() {
        BlazeLayout.render('layout', { main: 'username' });
    }
});

appRoutes.route('/telluswhatyouknownow', {
    name: 'telluswhatyouknownow',
    action: function() {
        BlazeLayout.render('layout', { main: 'telluswhatyouknownow' });
    }
});

appRoutes.route('/trial', {
    name: 'trial',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            if (Meteor.userAsync()) {
                BlazeLayout.render('layout', {
                    main: 'trial',
                    data: { type: "pre" }
                });
            }
        } catch (e) {
            console.error("Error in /trial route:", e);
        }
    }
});

appRoutes.route('/survey', {
    name: 'survey',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            if (Meteor.userAsync()) {
                BlazeLayout.render('layout', {
                    main: 'post_survey',
                    data: { type: "post" }
                });
            }
        } catch (e) {
            console.error("Error in /survey route:", e);
        }
    }
});

appRoutes.route('/check', {
    name: 'check',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            if (Meteor.userAsync()) {
                BlazeLayout.render('layout', {
                    main: 'trial',
                    data: { type: "post" }
                });
            }
        } catch (e) {
            console.error("Error in /check route:", e);
        }
    }
});

appRoutes.route('/posttest', {
    name: 'posttest',
    action: function() {
        BlazeLayout.render('layout', { main: 'posttest' });
    }
});

appRoutes.route('/welcome_step2', {
    name: 'welcome_step2',
    action: function() {
        BlazeLayout.render('layout', { main: 'welcome_step2' });
    }
});

appRoutes.route('/t/:name', {
    name: 'tag', // Using 'tag' as the route name based on your render
    action: function(params) {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            // if (Meteor.userAsync()?.profile?.questions?.length == 1 && Meteor.userAsync()?.profile?.intro_completed) {
            //     FlowRouter.go('/addq');
            //     showToast('You need to add one other question before accessing the entire Gut Instinct content', 4000);
            //     return;
            // }
            if (Meteor.userAsync()) {
                BlazeLayout.render('layout', {
                    main: 'tag',
                    data: {
                        name: params.name,
                        user: Meteor.userAsync().username
                    }
                });
            }
        } catch (e) {
            console.error("Error in /t/:name route:", e);
        }
    }
});

appRoutes.route('/personal_question/:name', {
    name: 'personal_question',
    action: function(params) {
        BlazeLayout.render('layout', {
            main: 'personal_tag_question',
            data: {
                name: params.name
            }
        });
    }
});

appRoutes.route('/personal/:name', {
    name: 'personal_page', // Using a different name to distinguish from personal_question/:name
    action: function(params) {
        BlazeLayout.render('layout', {
            main: 'personal_tag_question',
            data: {
                name: params.name
            }
        });
    }
});

appRoutes.route('/guide_question', {
    name: 'guide_question',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            if (Meteor.userAsync()) {
                const userProfile = Meteor.userAsync().profile;
                const condition = userProfile.condition;
                if ([3, 4, 5, 6, 0, 10, 11].includes(condition)) {
                    BlazeLayout.render('layout', {
                        main: 'guide_question_info',
                        data: { name: Meteor.userAsync().username }
                    });
                }
            }
        } catch (e) {
            console.error("Error in /guide_question route:", e);
        }
    }
});

appRoutes.route('/guide', {
    name: 'guide',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            if (Meteor.userAsync()) {
                BlazeLayout.render('layout', {
                    main: 'guide_question_welcome',
                    data: { name: Meteor.userAsync().username }
                });
            }
        } catch (e) {
            console.error("Error in /guide route:", e);
        }
    }
});

appRoutes.route('/guide_bin', {
    name: 'guide_bin',
    action: function() {
        BlazeLayout.render('layout', { main: 'guide_question_bin' });
    }
});

appRoutes.route('/guide_result', {
    name: 'guide_result',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            if (Meteor.userAsync()) {
                const condition = Meteor.userAsync().profile.condition;
                if ([3, 4, 5, 6, 0, 10, 11].includes(condition)) {
                    BlazeLayout.render('layout', { main: 'guide_question_result' });
                }
            }
        } catch (e) {
            console.error("Error in /guide_result route:", e);
        }
    }
});

appRoutes.route('/personal_welcome', {
    name: 'personal_welcome',
    action: function() {
        BlazeLayout.render('layout', { main: 'personal_question_bin' });
    }
});

appRoutes.route('/q/:hashcode', {
    name: 'question',
    action: function(params) {
        BlazeLayout.render('layout', {
            main: 'question',
            data: { hashcode: params.hashcode }
        });
    }
});

appRoutes.route('/p/:hashcode', {
    name: 'learn_problem',
    action: function(params) {
        BlazeLayout.render('layout', {
            main: 'learn_problem',
            data: { hashcode: params.hashcode }
        } );
    }
});

FlowRouter.route('/logout', { // This route is outside appRoutes because it handles logout before triggers
    name: 'logout',
    action: function() {
        BlazeLayout.render('layout', { main: 'loading_wheel' }); // Show loading immediately
        Meteor.call('galileo.profile.setMendel', localStorage.getItem('mendelcode_ga'), function(error, result) {
            Meteor.logout(function(err) {
                if (err || error) console.error('Error logging out:', err || error);
            });
            sessionStorage.clear();
            localStorage.clear();
            FlowRouter.go('/galileo/home'); // Redirect after logout
        });
    }
});

FlowRouter.route('/test', { // Assuming this is a utility/dev route, might not need full appRoutes triggers
    name: 'test',
    action: function() {
        BlazeLayout.render('layout', { main: 'test' });
    }
});

FlowRouter.route('/landing', { // This is an exclusion from appRoutes
    name: 'landing',
    action: function(params) {
        let landingURL = "";
        if (params.query.accessURL === '/login-bin/landing.html') {
            landingURL = '/login-bin';
        } else {
            landingURL = '/login-bin/landing.html?redirectAccess=' + params.query.accessURL;
        }
        // localStorage.setItem("condition", params.query.condition); // Uncomment if needed
        FlowRouter.go(landingURL);
    }
});

appRoutes.route('/intro', {
    name: 'intro',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            if (Meteor.userAsync()) {
                const userProfile = Meteor.userAsync().profile;
                if (userProfile.intro_completed) {
                    FlowRouter.go('/gutboard');
                    return;
                }
                let redirectURL = "/intro-bin/intro.html";
                if (userProfile.condition) {
                    const condition = userProfile.condition;
                    if (condition == 1 || condition == 8) redirectURL = "/intro-bin/index.html";
                    else if (condition == 2 || condition == 9) redirectURL = "/intro-bin/main.html";
                    else if (condition == 3 || condition == 5 || condition == 10) redirectURL = "/intro-bin/global.html";
                    else if (condition == 4 || condition == 6 || condition == 11) redirectURL = "/intro-bin/intro.html";
                    else if (condition == 7) redirectURL = "/intro-bin/introduction.html";
                }
                FlowRouter.go(redirectURL);
            }
        } catch (e) {
            console.error("Error in /intro route:", e);
        }
    }
});

FlowRouter.route('/login-error', { // This is an exclusion from appRoutes
    name: 'login-error',
    action: function() {
        FlowRouter.go('/login-bin/landing.html?status=101');
    }
});

FlowRouter.route('/login-process', { // This is an exclusion from appRoutes
    name: 'login-process',
    action: function(params) {
        BlazeLayout.render('layout', { main: 'loading_wheel' });

        // Note: promiseWait and CryptoJS are not standard Meteor/FlowRouter patterns for routes.
        // If CryptoJS is available globally, it might work.
        // For the promiseWait, FlowRouter actions are synchronous. If you need a delay,
        // it's usually done before setting the data or rendering, or by wrapping async calls.
        // This direct use of `promiseWait` inside an action might not behave as expected.
        // I'm keeping it as close to your original as possible, but be aware.
        function promiseWait(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        const username = CryptoJS.AES.decrypt(params.query.hWf5Ae4xvLMxSQYN, "82rSvyNZRpdvsEJw").toString(CryptoJS.enc.Utf8);
        const password = CryptoJS.AES.decrypt(params.query.FsheDddeK7c6UbEe, "82rSvyNZRpdvsEJw").toString(CryptoJS.enc.Utf8);
        const redirectRouting = params.query.redirectURL;
        let userRedirect = redirectRouting !== 'coldbrew';

        promiseWait(2000).then(() => {
            Meteor.loginWithPassword(username, password, function(err) {
                if (err) {
                    FlowRouter.go('/login-error');
                } else {
                    const userProfile = Meteor.userAsync()?.profile; // Get user profile AFTER login
                    if (!userProfile?.consent_agreed) {
                        FlowRouter.go('/consent');
                    } else {
                        if (userRedirect) {
                            FlowRouter.go(redirectRouting);
                        } else {
                            FlowRouter.go("/welcome");
                        }
                    }
                }
            });
        }).catch(e => {
            console.error("Error in login-process promiseWait:", e);
            FlowRouter.go('/login-error'); // Handle potential errors from promiseWait if it throws
        });
    }
});

appRoutes.route('/entrance', {
    name: 'entrance',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            if (Meteor.userAsync()) {
                const condition = Meteor.userAsync().profile.condition;
                if (condition == 7 && Meteor.userAsync().profile.guide_completed) FlowRouter.go('/topics');
                else if (condition == 7 && !Meteor.userAsync().profile.guide_completed) FlowRouter.go('/guide');
                else BlazeLayout.render('layout', { main: 'entrance' });
            }
        } catch (e) {
            console.error("Error in /entrance route:", e);
        }
    }
});

appRoutes.route('/profile', {
    name: 'profile',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            // if (Meteor.userAsync()?.profile?.questions?.length == 1 && Meteor.userAsync()?.profile?.intro_completed) {
            //     FlowRouter.go('/addq');
            //     showToast('You need to add one other question before accessing the entire Gut Instinct content', 4000);
            //     return;
            // }
            if (Meteor.userAsync()) {
                BlazeLayout.render('layout', { main: 'profile' });
            }
        } catch (e) {
            console.error("Error in /profile route:", e);
        }
    }
});

appRoutes.route('/topics', {
    name: 'topics',
    action: function() {
        try {
            if (checkUserProfileAndRedirect(FlowRouter.go)) {
                return;
            }
            // if (Meteor.userAsync()?.profile?.questions?.length == 1 && Meteor.userAsync()?.profile?.intro_completed) {
            //     FlowRouter.go('/addq');
            //     showToast('You need to add one other question before accessing the entire Gut Instinct content', 4000);
            //     return;
            // }
            if (Meteor.userAsync()) {
                const condition = Meteor.userAsync().profile.condition;
                if ([2, 4, 6, 7, 0, 9, 11].includes(condition)) {
                    BlazeLayout.render('layout', { main: 'topics' });
                }
            }
        } catch (e) {
            console.error("Error in /topics route:", e);
        }
    }
});

FlowRouter.route('/reset-password/:token', { // This is an exclusion from appRoutes
    name: 'reset-password',
    action: function(params) {
        BlazeLayout.render('layout', {
            main: 'reset_password',
            data: { token: params.token }
        });
    }
});

appRoutes.route('/galileo/visualization', {
    name: 'galileo.visualization',
    action: function() {
        BlazeLayout.render('layout', { main: 'emperorVisualization' });
    }
});


// Define other excluded routes explicitly if they need specific actions
// For example, if 'galileo.home' is a real route with a template
FlowRouter.route('/galileo/home', {
    name: 'galileo.home',
    action: function() {
        BlazeLayout.render('layout', { main: 'home' }); // Or your specific Galileo home template
    }
});

// Add other routes from the `except` list if they are expected to render content
// For example:
// FlowRouter.route('/galileo/signup', { name: 'galileo.signup', action: function() { BlazeLayout.render('layout', { main: 'galileo_signup_template' }); } });
// ... and so on for all your named routes in the 'except' list