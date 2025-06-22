import { Meteor } from 'meteor/meteor';
import { Experiments } from './experiments';
import { Pilots } from './pilot';
import { Participations } from './run';
import { ExperimentStatus, ParticipationStatus } from './constants';

const PHONE_NUM_REGEX = /^\d{10}$/;

const NUM_CONDITIONS = 2;
const DEFAULT_PROFILE = {
    condition: 0,
    //permission_group: PERMISSION.SUDO_ADMIN,
    consent_agreed: false,
    toured: {
        articles: false,
        bookmark: false,
        consent: false,
        username_page: false,
        guide_question_bin: false,
        guide_question_info: false,
        guide_question_module: false,
        guide_question_result: false,
        gutboard: false,
        gutboard_slider: false,
        landing: false,
        learn_discussions: false,
        personal_question: false,
        personal_question_bin: false,
        personal_question_module: false,
        personal_tag_question: false,
        problems: false,
        qmodule: false,
        tag: false,
        topics: false,
        tutorial: false,
        welcome_step2: false
    },
    topics_investigated: {},
    answered: {},
    discussed: {},
    voted: {},
    learn_questions_viewed: {},
    learn_questions_answered: {},
    learn_questions_discussed: {}
};

const DEFAULT_GALILEO_PROFILE = {
    notification: {
        onMyExp: true,
        onFollowingExp: true,
        onJoinedExp: true,
        onFeedbackProvidedExp: true,
        onNewExpAdded: true
    },
    tour: {
        started: false,
        finish_notified: false,
        progress: {
            pretest: false,
            intuition: false,
            intuition_board: false,
            create: false,
            feedback: false,
            pilot: false,
            run: false
        },
        selected_intuition_id: undefined,
        designed_experiment_id: undefined
    },
    feedback_experiments: [],
    finishedEthicsTraining: true // TODO remove once ethics is complete
};

async function fetchUser() {
    try {
        const currentUser = await Meteor.userAsync();
        return currentUser;
    } catch (error) {
        console.error("Error fetching user:", error);
        return null;
    }
}

Meteor.methods({
    'galileo.profile.setMendel': async function (mendel) {
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'mendelcode_ga': mendel
            }
        });
    },

    'galileo.profile.getMendel': async function () {
        const mendel = await Meteor.users.find({
            _id: Meteor.userId()
        }, {
            fields: {
                'mendelcode_ga': 1
            }
        }).fetchAsync();

        if (mendel.length > 0) {
            return mendel[0].mendelcode_ga;
        } else {
            return "";
        }
    },

    'galileo.profile.hasProfile': async function () {
        // Check user authorized
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        // Check if galileo exists in user object
        const user = await Meteor.userAsync();
        return ('galileo' in user);
    },

    'galileo.profile.isAdmin': async function () {
        // Check user authorized
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        // Check if galileo exists in user object
        const user = await Meteor.userAsync();
        return (user && user.profile && user.profile.is_admin);
    },

    'galileo.profile.hasPhoneNumber': async function (expId) {
        const userId = Meteor.userId();
        const users = await Meteor.users.find({
            _id: userId
        }, {
            fields: {
                "galileo.phone": 1,
                "galileo.remindByEmail": 1
            },
            limit: 1
        }).fetchAsync();

        if (!users || users.length === 0) {
            //this is a bug on our part -- maybe we deleted something on the db we shouldn't have
            throw new Meteor.Error("Oops, we cannot find your account in our database. Please email us at gutinstinct@ucsd.edu");
        }

        const user = users[0];
        if (!user.galileo || (!user.galileo.remindByEmail && (!user.galileo.phone || user.galileo.phone === ""))) {
            return false;
        }
        return true;
    },

    'galileo.profile.hasUsername': async function (userId) {
        const users = await Meteor.users.find({
            _id: userId
        }, {
            fields: {
                "username": 1
            },
            limit: 1
        }).fetchAsync();
        
        const user = users[0];
        if (!user || !user.username || user.username === "") {
            return false;
        }
        return true;
    },

    'galileo.profile.hasEmail': async function (userId) {
        const users = await Meteor.users.find({
            _id: userId
        }, {
            fields: {
                "emails": 1
            },
            limit: 1
        }).fetchAsync();
        
        const user = users[0];
        if (!user || !user.emails || user.emails[0].address === "") {
            return false;
        }
        return true;
    },

    'galileo.profile.updateProfile': async function () {
        // Check user authorized
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        // Check if the galileo profile has already existed
        const user = await Meteor.userAsync();
        if ('galileo' in user) {
            return;
        }

        // Generate random condition for the user
        const setprofobj = JSON.parse(JSON.stringify(DEFAULT_PROFILE));
        const setobj = JSON.parse(JSON.stringify(DEFAULT_GALILEO_PROFILE));
        setobj.condition = Math.floor(Math.random() * NUM_CONDITIONS);

        // Get the current user and add the default galileo profile
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                'galileo': setobj,
                'profile': setprofobj
            }
        });
        
        const updatedUser = await Meteor.userAsync();
        if ('galileo' in updatedUser) {
            console.log("GALILEO ADDED");
        } else {
            console.log("GALILEO NOT ADDED");
        }
    },

    //whatsapp implementation
    'galileo.getUserByPhoneNumber': async function (phone) {
        if (phone.includes("whatsapp:")) {
            const whatsapp = await Meteor.users.findOneAsync({
                "galileo.phone": phone
            });
            return whatsapp;
        } else {
            const reg_phone = await Meteor.users.findOneAsync({
                "galileo.phone": phone.substring(2)
            });
            return reg_phone;
        }
    },

    'galileo.profile.deleteProfile': async function () {
        await Meteor.users.updateAsync(Meteor.userId(), {
            $unset: {
                'galileo': ""
            }
        });
    },

    'galileo.profile.getProfile': async function(user_id) {
        // Check user authorized
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        if (user_id === undefined || user_id === null) {
            user_id = Meteor.userId();
        }

        const user = await Meteor.users.findOneAsync({
            _id: user_id
        });
        
        return user ? user.profile : null;
    },

    'galileo.profile.getCtryFlagByArray': async function (id_array) {
        const result = [];
        for (const elt of id_array) {
            const flag = await getFlagHelper("", elt);
            result.push(flag);
        }
        return result;
    },

    'galileo.profile.getCtryFlag': async function (username, user_id) {
        return await getFlagHelper(username, user_id);
    },

    'galileo.profile.getExperimentStatsSidebar': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        const [
            unfin,
            create,
            review,
            participate,
            comp,
            ongoing,
            readyToRun,
            underReview
        ] = await Promise.all([
            Meteor.callAsync("galileo.profile.getUnfinishedExperiments"),
            Meteor.callAsync("galileo.profile.getCreatedExperiments"),
            Meteor.callAsync('galileo.profile.getReviewingExperiments'),
            Meteor.callAsync("galileo.profile.getParticipatingExperiments"),
            Meteor.callAsync("galileo.profile.getCompletedExperiments"),
            Meteor.callAsync("galileo.profile.getOngoingExperiments"),
            Meteor.callAsync("galileo.profile.getReadyToRunExperiments"),
            Meteor.callAsync("galileo.profile.getUnderReviewExperiments")
        ]);

        const expStats = {
            unfinishedExps: unfin.length,
            createdExps: create.length,
            reviewingExps: review.length,
            participatingExps: participate.length,
            completedExps: comp.length,
            ongoingExps: ongoing.length,
            readyToRunExps: readyToRun.length,
            underReviewExps: underReview.length
        }

        return expStats;
    },

    'galileo.profile.getUnderReviewExperiments': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        const experimentsArray = await Experiments.find({
            "user_id": Meteor.userId(),
            "status": {
                $gte: ExperimentStatus.OPEN_FOR_REVIEW,
                $lte: ExperimentStatus.REVIEWED
            }
        }, {
            fields: {
                "_id": 1
            },
            sort: {
                "create_date_time": -1
            }
        }).fetchAsync();

        const experiments = await Promise.all(
            experimentsArray.map(exp => Meteor.callAsync("galileo.experiments.getExperiment", exp._id))
        );

        return experiments;
    },

    'galileo.profile.getReadyToRunExperiments': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        const experimentsArray = await Experiments.find({
            "user_id": Meteor.userId(),
            "status": ExperimentStatus.READY_TO_RUN
        }, {
            fields: {
                "_id": 1
            },
            sort: {
                "create_date_time": -1
            }
        }).fetchAsync();

        const experiments = await Promise.all(
            experimentsArray.map(exp => Meteor.callAsync("galileo.experiments.getExperiment", exp._id))
        );

        return experiments;
    },

    'galileo.profile.getCreatedExperiments': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        const experimentsArray = await Experiments.find({
            "user_id": Meteor.userId(),
            "status": {
                $gte: ExperimentStatus.DESIGNED
            }
        }, {
            fields: {
                "_id": 1
            },
            sort: {
                "create_date_time": -1
            }
        }).fetchAsync();

        const experiments = await Promise.all(
            experimentsArray.map(exp => Meteor.callAsync("galileo.experiments.getExperiment", exp._id))
        );

        return experiments;
    },

    'galileo.profile.getCompletedExperiments': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        const experimentsArray = await Experiments.find({
            "user_id": Meteor.userId(),
            "status": {
                $gte: ExperimentStatus.FINISHED
            }
        }, {
            fields: {
                "_id": 1
            },
            sort: {
                "create_date_time": -1
            }
        }).fetchAsync();

        const experiments = await Promise.all(
            experimentsArray.map(exp => Meteor.callAsync("galileo.experiments.getExperiment", exp._id))
        );

        return experiments;
    },

    'galileo.profile.getOngoingExperiments': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        const experimentsArray = await Experiments.find({
            "user_id": Meteor.userId(),
            "status": {
                $gte: ExperimentStatus.PREPARING_TO_START,
                $lt: ExperimentStatus.FINISHED
            }
        }, {
            fields: {
                "_id": 1
            },
            sort: {
                "create_date_time": -1
            }
        }).fetchAsync();

        const experiments = await Promise.all(
            experimentsArray.map(exp => Meteor.callAsync("galileo.experiments.getExperiment", exp._id))
        );

        return experiments;
    },

    'galileo.profile.getPilotingExperiments': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }

        const expMap = {};

        const pilots = await Pilots.find({
            user_id: Meteor.userId()
        }, {
            fields: {
                _id: 1,
                exp_id: 1
            },
            sort: {
                user_endDate_inGmt: -1
            }
        }).fetchAsync();

        for (const pilot of pilots) {
            if (!expMap[pilot.exp_id]) {
                expMap[pilot.exp_id] = await Meteor.callAsync("galileo.experiments.getExperiment", pilot.exp_id);
            }
        }

        return Object.values(expMap);
    },

    'galileo.profile.getUnfinishedExperiments': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }

        const experimentsArray = await Experiments.find({
            "user_id": Meteor.userId(),
            "status": ExperimentStatus.CREATED
        }, {
            fields: {
                _id: 1
            }
        }).fetchAsync();

        const experiments = await Promise.all(
            experimentsArray.map(exp => Meteor.callAsync("galileo.experiments.getExperiment", exp._id))
        );

        return experiments;
    },

    'galileo.profile.getReviewingExperiments': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }

        const users = await Meteor.users.find({
            _id: Meteor.userId()
        }, {
            fields: {
                "galileo.feedback_experiments": 1
            }
        }).fetchAsync();

        if (users && users.length > 0) {
            const user = users[0];
            if (user && user.galileo && user.galileo.feedback_experiments && user.galileo.feedback_experiments.length > 0) {
                const experiments = await Promise.all(
                    user.galileo.feedback_experiments.map(async (exp_id) => {
                        return await Meteor.callAsync("galileo.experiments.getExperiment", exp_id);
                    })
                );
                
                return experiments.filter((exp) => {
                    return exp; //to remove undefined or null values
                });
            } else {
                return [];
            }
        }
        return [];
    },

    'galileo.profile.getParticipatingExperiments': async function () {
        const participationsArray = await Participations.find({
            "user_id": Meteor.userId()
        }, {
            fields: {
                "exp_id": 1
            }
        }).fetchAsync();

        const experiments = await Promise.all(
            participationsArray.map(exp => Meteor.callAsync("galileo.experiments.getExperiment", exp.exp_id))
        );

        return experiments;
    },

    'galileo.profile.getPhone': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        const user = await Meteor.userAsync();
        if (!user) {
            throw new Meteor.Error("user-not-exists");
        }
        
        if (!user.galileo || !user.galileo.phone || user.galileo.phone === "") {
            return undefined;
        } else {
            return user.galileo.phone;
        }
    },

    'galileo.profile.setPhone': async function (phone) {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        phone = phone.trim();
        if (!phone.match(PHONE_NUM_REGEX)) {
            throw new Meteor.Error('Invalid Phone Number');
        }

        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.phone": phone
            }
        });
    },

    'galileo.profile.setEmail': async function (email) {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "emails": [{
                    "address": email,
                    "verified": false
                }]
            }
        });
    },

    'galileo.profile.setUsername': async function (username) {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "username": username
            }
        });
    },

    'galileo.profile.setEmailReminder': async function (boolVal) {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.remindByEmail": boolVal
            }
        });
    },

    'galileo.profile.setCountry': async function (country) {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.country": country
            }
        });
    },

    'galileo.profile.setCity': async function (city) {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.city": city
            }
        });
    },

    'galileo.profile.setTimeZone': async function (timezone, isDst) {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.timezone": timezone,
                "galileo.isDst": isDst
            }
        });
    },

    'galileo.profile.setTimeZoneOnly': async function (timezone) {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.timezone": timezone,
            }
        });
    },

    'galileo.profile.setIsDstOnly': async function (isDst) {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.isDst": isDst,
            }
        });
    },

    'galileo.profile.setInterest': async function (interest) {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.interest": interest
            }
        });
    },

    'galileo.profile.getInterest': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        const user = await Meteor.userAsync();
        return user.galileo.interest;
    },

    // TODO Deprecated
    'galileo.profile.setIntuitionTime': async function (time) {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                "galileo.intuitionTime": time
            }
        });
    },

    'users.hasUsername': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        const user = await Meteor.userAsync();
        return user.username !== undefined;
    },

    'users.getUsername': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }

        const user = await Meteor.userAsync();
        return user.username;
    },

    // TODO @Vineet
    'galileo.profile.updateEthicsCertificate': async function (url) {
        const currentUserId = Meteor.userId();
        if (!currentUserId) {
            throw new Meteor.Error("not-authorized");
        }
        
        await Meteor.users.updateAsync(currentUserId, {
            $set: {
                "galileo.ethicsCertificate": url,
                "galileo.finishedEthicsTraining": true
            }
        });

        //update all experiments created by user that were "designed" to become "open for review"
        await Experiments.updateAsync({
            user_id: currentUserId,
            status: ExperimentStatus.DESIGNED
        }, {
            $set: {
                status: ExperimentStatus.OPEN_FOR_REVIEW
            }
        });
    },

    'galileo.profile.getEthicsCertificate': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error("not-authorized");
        }
        
        const user = await Meteor.userAsync();
        if (!user) {
            throw new Meteor.Error("user-not-found");
        }
        
        if (user.galileo && user.galileo.ethicsCertificate) {
            return user.galileo.ethicsCertificate;
        } else {
            return undefined;
        }
    },

    'galileo.profile.hasFinishedEthics': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized')
        }
        
        const user = await Meteor.userAsync();
        return user.galileo.finishedEthicsTraining;
    },

    'galileo.profile.setUsernameToured': async function () {
        console.log('marking username toured = true');
        await Meteor.users.updateAsync(Meteor.userId(), {
            $set: {
                'profile.toured.username_page': true
            }
        });
    },

    'galileo.profile.getNotificationSetting': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        const user = await Meteor.userAsync();
        return user.galileo.notification;
    },

    'galileo.profile.notification.enableOnMyExp': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onMyExp': true
            }
        });
    },

    'galileo.profile.notification.disableOnMyExp': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onMyExp': false
            }
        });
    },

    'galileo.profile.notification.enableOnFollowingExp': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onFollowingExp': true
            }
        });
    },

    'galileo.profile.notification.disableOnFollowingExp': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onFollowingExp': false
            }
        });
    },

    'galileo.profile.notification.enableOnJoinedExp': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onJoinedExp': true
            }
        });
    },

    'galileo.profile.notification.disableOnJoinedExp': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onJoinedExp': false
            }
        });
    },

    'galileo.profile.notification.enableOnFeedbackProvidedExp': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onFeedbackProvidedExp': true
            }
        });
    },

    'galileo.profile.notification.disableOnFeedbackProvidedExp': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onFeedbackProvidedExp': false
            }
        });
    },

    'galileo.profile.notification.enableOnNewExpAdded': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onNewExpAdded': true
            }
        });
    },

    'galileo.profile.notification.disableOnNewExpAdded': async function () {
        if (!Meteor.userId()) {
            throw new Meteor.Error('not-authorized');
        }
        
        await Meteor.users.updateAsync({
            _id: Meteor.userId()
        }, {
            $set: {
                'galileo.notification.onNewExpAdded': false
            }
        });
    },

    'galileo.profile.getRelativeExperiments': async function (userId) {
        const relativeExps = [];
        
        // Get experiments by user
        const exps = await getExperimentsByUserHelper(userId);
        relativeExps.push(...exps);
        
        // Get reviewing experiments
        const reviewing = await Experiments.find({
            feedback_users: userId,
            status: {
                $gte: ExperimentStatus.OPEN_FOR_REVIEW,
                $lte: ExperimentStatus.REVIEWED
            }
        }).fetchAsync();
        relativeExps.push(...reviewing);
        
        // Get participations
        const participations = await Participations.find({
            user_id: userId,
            status: {
                $gte: ParticipationStatus.PASSED_CRITERIA,
                $lte: ParticipationStatus.FINISHED,
            }
        }).fetchAsync();
        relativeExps.push(...participations);
        
        return relativeExps;
    },
});

async function getExperimentsByUserHelper(targetUserID) {
    if (!targetUserID) {
        return null;
    }
    
    return new Promise((resolve, reject) => {
        Experiments.rawCollection().aggregate([
            {
                $match: {
                    user_id: targetUserID
                }
            },
            {
                $lookup: {
                    from: "ga_experiment_designs",
                    localField: "curr_design_id",
                    foreignField: "_id",
                    as: "design"
                }
            },
            {
                $unwind: "$design"
            }
        ], (error, result) => {
            if (error) {
                reject(error);
            } else {
                resolve(result);
            }
        });
    });
}

async function getFlagHelper(username, user_id) {
    let ctry = "";
    
    if (username && username.length > 0) {
        const user = await Meteor.users.findOneAsync({ "username": username });
        ctry = user?.galileo?.country || "";
    } else {
        const user = await Meteor.users.findOneAsync(user_id);
        ctry = user?.galileo?.country || "";
    }

  if (!countryCode) return "";

    const countryMap = {
        USA: 'us', CHN: 'cn', MNE: 'me', BRA: 'br', NZL: 'nz', CAN: 'ca',
        GBR: 'gb', IND: 'in', EGY: 'eg', AUS: 'au', ESP: 'es', NLD: 'nl',
        DNK: 'dk', ITA: 'it'
    };
    
    return `flag-icon-${countryMap[countryCode] || 'aw'}`; // 'aw' as default for unknown codes


}
