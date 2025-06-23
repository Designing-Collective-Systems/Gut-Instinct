import { FlowRouter } from 'meteor/kadira:flow-router';
import { BlazeLayout } from 'meteor/kadira:blaze-layout';
import { Tracker } from 'meteor/tracker';

// Import your collections (models.js)
import {
    UserMetrics,
    UserEmail,
    UserTestResponse
} from './models.js';

// Assuming you still need this for GA tracking
import './ga-routes.js';

// --- Global Before Action (Authentication Guard) ---
const checkLoggedIn = function(context, redirect) {
    // Don't render anything here - let individual routes handle their rendering
    
    // Use Tracker.autorun for reactive computation
    Tracker.autorun((computation) => {
        const user = Meteor.user();
        const loggingIn = Meteor.loggingIn();
        
        if (!user && !loggingIn) {
            computation.stop();
            redirect('/galileo/home');
        } else if (user) {
            computation.stop();
            // User is logged in, continue with route
        }
        // If loggingIn is true, keep waiting
    });
};

// Define routes that do not require authentication
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

// Create authenticated routes group
const authenticatedRoutes = FlowRouter.group({
    triggersEnter: [checkLoggedIn]
});

// Create public routes group (no authentication required)
const publicRoutes = FlowRouter.group({});

// --- Helper for Profile-based Redirects ---
const checkUserProfileAndRedirect = function() {
    const user = Meteor.user();
    if (!user) {
        FlowRouter.go('/galileo/home');
        return true;
    }
    
    const profile = user.profile;
    if (!profile) {
        return false;
    }

    if (!profile.consent_agreed) {
        FlowRouter.go('/consent');
        return true;
    }
    if (!profile.toured?.username_page) {
        FlowRouter.go('/username');
        return true;
    }
    if (!profile.took_pretest) {
        FlowRouter.go('/trial');
        return true;
    }
    if (!profile.intro_completed) {
        const docentProgress = localStorage.getItem("docentProgress");
        if (docentProgress && (docentProgress == 25 || docentProgress == 50)) {
            FlowRouter.go('/t/introduction');
            return true;
        }
        if (docentProgress && docentProgress == 85) {
            FlowRouter.go('/gutboard_slider_addq');
            return true;
        }
        FlowRouter.go('/guide');
        return true;
    }
    return false;
};

// Function for toast messages
const showToast = (message, duration = 4000) => {
    if (typeof Materialize !== 'undefined' && Materialize.toast) {
        Materialize.toast(message, duration, 'toast');
    } else {
        console.warn("Materialize.toast is not available. Message:", message);
    }
};

// --- ROUTES ---

// Root Redirect
FlowRouter.route('/', {
    name: 'root',
    action() {
        FlowRouter.go('/galileo');
    }
});

// Main galileo route
FlowRouter.route('/galileo', {
    name: 'galileo.home_redirect',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            const loggingIn = Meteor.loggingIn();
            
            if (loggingIn) {
                BlazeLayout.render('layout', { main: 'loading_wheel' });
                return;
            }
            
            computation.stop();
            
            if (user) {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                if (user.profile.condition == 7) {
                    FlowRouter.go('/topics');
                } else {
                    FlowRouter.go('/gutboard');
                }
            } else {
                console.log("Meteor-user0");
                BlazeLayout.render('layout', { main: 'home' });
            }
        });
    }
});

// Public routes
publicRoutes.route('/login-admin', {
    name: 'login-admin',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            const loggingIn = Meteor.loggingIn();
            
            if (loggingIn) {
                BlazeLayout.render('layout', { main: 'loading_wheel' });
                return;
            }
            
            computation.stop();
            
            if (!user) {
                BlazeLayout.render('layout', { main: 'login' });
            } else {
                FlowRouter.go('/consent');
            }
        });
    }
});

publicRoutes.route('/signup', {
    name: 'signup',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            const loggingIn = Meteor.loggingIn();
            
            if (loggingIn) {
                BlazeLayout.render('layout', { main: 'loading_wheel' });
                return;
            }
            
            computation.stop();
            
            if (!user) {
                BlazeLayout.render('layout', { main: 'signup' });
            } else {
                BlazeLayout.render('layout', { main: 'loading_wheel' });
                FlowRouter.go('/galileo/consent');
            }
        });
    }
});

publicRoutes.route('/login-admin1', {
    name: 'login-admin1',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            const loggingIn = Meteor.loggingIn();
            
            if (loggingIn) {
                BlazeLayout.render('layout', { main: 'loading_wheel' });
                return;
            }
            
            computation.stop();
            
            if (!user) {
                BlazeLayout.render('layout', { main: 'new_login' });
            } else {
                FlowRouter.go('/consent');
            }
        });
    }
});

// Authenticated routes
authenticatedRoutes.route('/consent', {
    name: 'consent',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return; // Will be handled by triggersEnter
            
            computation.stop();
            
            if (!user.profile?.consent_agreed) {
                Meteor.call("galileo.profile.updateProfile");
                BlazeLayout.render('layout', { main: 'consent' });
            } else {
                FlowRouter.go('/intro');
            }
        });
    }
});

authenticatedRoutes.route('/tutorial', {
    name: 'tutorial',
    action() {
        BlazeLayout.render('layout', { main: 'tutorial' });
    }
});

authenticatedRoutes.route('/gutboard', {
    name: 'gutboard',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                if (user.profile?.condition != 7) {
                    BlazeLayout.render('layout', {
                        main: 'gutboard_slider'
                    }, {
                        mendelcode: "AmericanGutProject"
                    });
                }
            } catch (e) {
                console.error("Error in /gutboard route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/gutboard/:mendelcode', {
    name: 'gutboard_with_code',
    action(params) {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                if (user.profile?.condition != 7) {
                    BlazeLayout.render('layout', {
                        main: 'gutboard_slider'
                    }, {
                        mendelcode: params.mendelcode
                    });
                }
            } catch (e) {
                console.error("Error in /gutboard/:mendelcode route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/gutboard/:mendelcode/search', {
    name: 'gutboard_search',
    action(params, queryParams) {
        BlazeLayout.render('layout', {
            main: 'gutboard_search'
        }, {
            mendelcode: params.mendelcode,
            searchQuery: queryParams.q
        });
    }
});

authenticatedRoutes.route('/addq', {
    name: 'addq',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }

                const userProfile = user.profile;
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
        });
    }
});

authenticatedRoutes.route('/gutboard_slider_addq', {
    name: 'gutboard_slider_addq',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }

                const userProfile = user.profile;
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
        });
    }
});

authenticatedRoutes.route('/gutboard_old', {
    name: 'gutboard_old',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            const condition = user.profile?.condition;
            if (condition == 1) {
                FlowRouter.go('/problems');
                return;
            }
            BlazeLayout.render('layout', { main: 'gutboard' });
        });
    }
});

authenticatedRoutes.route('/gutboard_slider', {
    name: 'gutboard_slider',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) {
                computation.stop();
                console.log("Meteor-userg");
                FlowRouter.go('/galileo/home');
                return;
            }
            
            computation.stop();

            if (checkUserProfileAndRedirect()) {
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
        });
    }
});

authenticatedRoutes.route('/problems', {
    name: 'problems',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            const condition = user.profile?.condition;
            if (condition != 1) {
                FlowRouter.go('/gutboard');
                return;
            }
            BlazeLayout.render('layout', { main: 'problems' });
        });
    }
});

authenticatedRoutes.route('/articles', {
    name: 'articles',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            const condition = user.profile?.condition;
            if (condition != 2) {
                FlowRouter.go('/gutboard');
                return;
            }
            BlazeLayout.render('layout', { main: 'articles' });
        });
    }
});

authenticatedRoutes.route('/bookmark', {
    name: 'bookmark',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            const condition = user.profile?.condition;
            if (false && condition != 1) {
                FlowRouter.go('/gutboard');
                return;
            }
            BlazeLayout.render('layout', { main: 'bookmark' });
        });
    }
});

authenticatedRoutes.route('/welcome', {
    name: 'welcome',
    action() {
        BlazeLayout.render('layout', { main: 'loading_wheel' });
        
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) {
                console.log("Meteor-userw");
                return;
            }

            computation.stop();
            
            const username = user.username;
            const TestResult = UserTestResponse.findOne({ "username": username });

            if (TestResult == undefined) {
                FlowRouter.go('/username');
            } else {
                FlowRouter.go('/gutboard');
            }
        });
    }
});

authenticatedRoutes.route('/welcome_uncheck', {
    name: 'welcome_uncheck',
    action() {
        Tracker.autorun((computation) => {
            const currentUser = Meteor.user();
            if (!currentUser) {
                computation.stop();
                FlowRouter.go('/galileo/home');
                return;
            }
            
            computation.stop();
            
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
        });
    }
});

authenticatedRoutes.route('/welcome_step1', {
    name: 'welcome_step1',
    action() {
        FlowRouter.go('/welcome_step2');
    }
});

authenticatedRoutes.route('/username', {
    name: 'username',
    action() {
        BlazeLayout.render('layout', { main: 'username' });
    }
});

authenticatedRoutes.route('/telluswhatyouknownow', {
    name: 'telluswhatyouknownow',
    action() {
        BlazeLayout.render('layout', { main: 'telluswhatyouknownow' });
    }
});

authenticatedRoutes.route('/trial', {
    name: 'trial',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                BlazeLayout.render('layout', {
                    main: 'trial'
                }, {
                    type: "pre"
                });
            } catch (e) {
                console.error("Error in /trial route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/survey', {
    name: 'survey',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                BlazeLayout.render('layout', {
                    main: 'post_survey'
                }, {
                    type: "post"
                });
            } catch (e) {
                console.error("Error in /survey route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/check', {
    name: 'check',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                BlazeLayout.render('layout', {
                    main: 'trial'
                }, {
                    type: "post"
                });
            } catch (e) {
                console.error("Error in /check route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/posttest', {
    name: 'posttest',
    action() {
        BlazeLayout.render('layout', { main: 'posttest' });
    }
});

authenticatedRoutes.route('/welcome_step2', {
    name: 'welcome_step2',
    action() {
        BlazeLayout.render('layout', { main: 'welcome_step2' });
    }
});

authenticatedRoutes.route('/t/:name', {
    name: 'tag',
    action(params) {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                BlazeLayout.render('layout', {
                    main: 'tag'
                }, {
                    name: params.name,
                    user: user.username
                });
            } catch (e) {
                console.error("Error in /t/:name route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/personal_question/:name', {
    name: 'personal_question',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'personal_tag_question'
        }, {
            name: params.name
        });
    }
});

authenticatedRoutes.route('/personal/:name', {
    name: 'personal_page',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'personal_tag_question'
        }, {
            name: params.name
        });
    }
});

authenticatedRoutes.route('/guide_question', {
    name: 'guide_question',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                const userProfile = user.profile;
                const condition = userProfile.condition;
                if ([3, 4, 5, 6, 0, 10, 11].includes(condition)) {
                    BlazeLayout.render('layout', {
                        main: 'guide_question_info'
                    }, {
                        name: user.username
                    });
                }
            } catch (e) {
                console.error("Error in /guide_question route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/guide', {
    name: 'guide',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                BlazeLayout.render('layout', {
                    main: 'guide_question_welcome'
                }, {
                    name: user.username
                });
            } catch (e) {
                console.error("Error in /guide route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/guide_bin', {
    name: 'guide_bin',
    action() {
        BlazeLayout.render('layout', { main: 'guide_question_bin' });
    }
});

authenticatedRoutes.route('/guide_result', {
    name: 'guide_result',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                const condition = user.profile.condition;
                if ([3, 4, 5, 6, 0, 10, 11].includes(condition)) {
                    BlazeLayout.render('layout', { main: 'guide_question_result' });
                }
            } catch (e) {
                console.error("Error in /guide_result route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/personal_welcome', {
    name: 'personal_welcome',
    action() {
        BlazeLayout.render('layout', { main: 'personal_question_bin' });
    }
});

authenticatedRoutes.route('/q/:hashcode', {
    name: 'question',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'question'
        }, {
            hashcode: params.hashcode
        });
    }
});

authenticatedRoutes.route('/p/:hashcode', {
    name: 'learn_problem',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'learn_problem'
        }, {
            hashcode: params.hashcode
        });
    }
});

// Public logout route
publicRoutes.route('/logout', {
    name: 'logout',
    action() {
        BlazeLayout.render('layout', { main: 'loading_wheel' });
        
        Meteor.call('galileo.profile.setMendel', localStorage.getItem('mendelcode_ga'), function(error, result) {
            Meteor.logout(function(err) {
                if (err || error) console.error('Error logging out:', err || error);
            });
            sessionStorage.clear();
            localStorage.clear();
            FlowRouter.go('/galileo/home');
        });
    }
});

// Test route
FlowRouter.route('/test', {
    name: 'test',
    action() {
        BlazeLayout.render('layout', { main: 'test' });
    }
});

// Landing route
publicRoutes.route('/landing', {
    name: 'landing',
    action(params, queryParams) {
        let landingURL = "";
        if (queryParams.accessURL === '/login-bin/landing.html') {
            landingURL = '/login-bin';
        } else {
            landingURL = '/login-bin/landing.html?redirectAccess=' + queryParams.accessURL;
        }
        FlowRouter.go(landingURL);
    }
});

authenticatedRoutes.route('/intro', {
    name: 'intro',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                const userProfile = user.profile;
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
            } catch (e) {
                console.error("Error in /intro route:", e);
            }
        });
    }
});

// Login error route
publicRoutes.route('/login-error', {
    name: 'login-error',
    action() {
        FlowRouter.go('/login-bin/landing.html?status=101');
    }
});

// Login process route
publicRoutes.route('/login-process', {
    name: 'login-process',
    action(params, queryParams) {
        BlazeLayout.render('layout', { main: 'loading_wheel' });

        function promiseWait(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        const username = CryptoJS.AES.decrypt(queryParams.hWf5Ae4xvLMxSQYN, "82rSvyNZRpdvsEJw").toString(CryptoJS.enc.Utf8);
        const password = CryptoJS.AES.decrypt(queryParams.FsheDddeK7c6UbEe, "82rSvyNZRpdvsEJw").toString(CryptoJS.enc.Utf8);
        const redirectRouting = queryParams.redirectURL;
        let userRedirect = redirectRouting !== 'coldbrew';

        promiseWait(2000).then(() => {
            Meteor.loginWithPassword(username, password, function(err) {
                if (err) {
                    FlowRouter.go('/login-error');
                } else {
                    const userProfile = Meteor.user()?.profile;
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
            FlowRouter.go('/login-error');
        });
    }
});

authenticatedRoutes.route('/entrance', {
    name: 'entrance',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                const condition = user.profile.condition;
                if (condition == 7 && user.profile.guide_completed) {
                    FlowRouter.go('/topics');
                } else if (condition == 7 && !user.profile.guide_completed) {
                    FlowRouter.go('/guide');
                } else {
                    BlazeLayout.render('layout', { main: 'entrance' });
                }
            } catch (e) {
                console.error("Error in /entrance route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/profile', {
    name: 'profile',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                BlazeLayout.render('layout', { main: 'profile' });
            } catch (e) {
                console.error("Error in /profile route:", e);
            }
        });
    }
});

authenticatedRoutes.route('/topics', {
    name: 'topics',
    action() {
        Tracker.autorun((computation) => {
            const user = Meteor.user();
            if (!user) return;
            
            computation.stop();
            
            try {
                if (checkUserProfileAndRedirect()) {
                    return;
                }
                
                const condition = user.profile.condition;
                if ([2, 4, 6, 7, 0, 9, 11].includes(condition)) {
                    BlazeLayout.render('layout', { main: 'topics' });
                }
            } catch (e) {
                console.error("Error in /topics route:", e);
            }
        });
    }
});

// Reset password route
publicRoutes.route('/reset-password/:token', {
    name: 'reset-password',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'reset_password'
        }, {
            token: params.token
        });
    }
});

authenticatedRoutes.route('/galileo/visualization', {
    name: 'galileo.visualization',
    action() {
        BlazeLayout.render('layout', { main: 'emperorVisualization' });
    }
});

// Galileo home route
publicRoutes.route('/galileo/home', {
    name: 'galileo.home',
    action() {
        BlazeLayout.render('layout', { main: 'home' });
    }
});

// Additional public routes that might need specific implementations
publicRoutes.route('/galileo/signup', {
    name: 'galileo.signup',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_signup' });
    }
});

publicRoutes.route('/galileo/landing', {
    name: 'galileo.landing',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_landing' });
    }
});

publicRoutes.route('/galileo/browse', {
    name: 'galileo.browse',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_browse' });
    }
});

publicRoutes.route('/galileo/experiment/:id?', {
    name: 'galileo.experiment',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'galileo_experiment'
        }, {
            experimentId: params.id
        });
    }
});

publicRoutes.route('/galileo/share/review/:id', {
    name: 'galileo.share.review',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'galileo_share_review'
        }, {
            experimentId: params.id
        });
    }
});

publicRoutes.route('/galileo/share/review/guest/:id', {
    name: 'galileo.share.review.guest',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'galileo_share_review_guest'
        }, {
            experimentId: params.id
        });
    }
});

publicRoutes.route('/galileo/experiment/feedback/:id', {
    name: 'galileo.experiment.feedback',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'galileo_experiment_feedback'
        }, {
            experimentId: params.id
        });
    }
});

publicRoutes.route('/galileo/join/consent/:id', {
    name: 'galileo.join.consent',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'galileo_join_consent'
        }, {
            experimentId: params.id
        });
    }
});

publicRoutes.route('/galileo/join', {
    name: 'galileo.join',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_join' });
    }
});

publicRoutes.route('/galileo/join/criteria/:id', {
    name: 'galileo.join.criteria',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'galileo_join_criteria'
        }, {
            experimentId: params.id
        });
    }
});

publicRoutes.route('/galileo/share/join/:id', {
    name: 'galileo.share.join',
    action(params) {
        BlazeLayout.render('layout', {
            main: 'galileo_share_join'
        }, {
            experimentId: params.id
        });
    }
});

// Blog routes
publicRoutes.route('/galileo/blog/why-exp', {
    name: 'galileo.blog.why-exp',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-openhumans', {
    name: 'galileo.blog.why-exp-openhumans',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_openhumans' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-lyme', {
    name: 'galileo.blog.why-exp-lyme',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_lyme' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-kefir', {
    name: 'galileo.blog.why-exp-kefir',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_kefir' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-T1D', {
    name: 'galileo.blog.why-exp-T1D',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_t1d' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-kombucha', {
    name: 'galileo.blog.why-exp-kombucha',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_kombucha' });
    }
});

publicRoutes.route('/galileo/blog/tutorial', {
    name: 'galileo.blog.tutorial',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_tutorial' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-agp', {
    name: 'galileo.blog.why-exp-agp',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_agp' });
    }
});

publicRoutes.route('/galileo/me/datasheet', {
    name: 'galileo.me.datasheet',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_me_datasheet' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-gut-check', {
    name: 'galileo.blog.why-exp-gut-check',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_gut_check' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-soylent', {
    name: 'galileo.blog.why-exp-soylent',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_soylent' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-diet', {
    name: 'galileo.blog.why-exp-diet',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_diet' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-beer', {
    name: 'galileo.blog.why-exp-beer',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_beer' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-spice', {
    name: 'galileo.blog.why-exp-spice',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_spice' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-circadian', {
    name: 'galileo.blog.why-exp-circadian',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_circadian' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-nerdnite', {
    name: 'galileo.blog.why-exp-nerdnite',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_nerdnite' });
    }
});

publicRoutes.route('/galileo/blog/why-exp-probiotics', {
    name: 'galileo.blog.why-exp-probiotics',
    action() {
        BlazeLayout.render('layout', { main: 'galileo_blog_why_exp_probiotics' });
    }
});

// Auth OpenHumans route
publicRoutes.route('/auth_openhumans', {
    name: 'auth_openhumans',
    action() {
        BlazeLayout.render('layout', { main: 'auth_openhumans' });
    }
});