import {
    ExperimentStatus,
    NotificationType,
    ParticipationStatus
} from './constants';
import { Meteor } from 'meteor/meteor';
import { Pilots } from './pilot';
import { Feedbacks } from "./feedback";
import { Participations } from "./run";
import { Time } from "./time";
import { ExperimentHelper } from "./commonExperimentHelpers";
import { HTTP } from 'meteor/http';

export const Experiments = new Mongo.Collection('ga_experiments');
export const ExperimentDesigns = new Mongo.Collection('ga_experiment_designs');

Meteor.methods({
    'galileo.experiments.sendEmail': async function (expId, type, msg, url, arg_temp) {
        console.log('in send email type = ' + type + ' msg = ' + msg + ' url = ' + url);
        const exp = await Meteor.callAsync("galileo.experiments.getExperiment", expId);
        
        if (exp) {
            const creatorName = exp.username;

            if (creatorName) {
                const user = await Meteor.userAsync();
                const otherUser = await Meteor.callAsync('galileo.run.getParticipantMap', expId, user);
                const expTitle = "Does " + exp.design.cause + " affect " + exp.design.effect + "?";

                let args = {
                    creatorName: creatorName,
                    expTitle: expTitle,
                    expId: expId,
                    otherUser: otherUser
                };

                if (arg_temp) {
                    args = Object.assign(args, arg_temp);
                }

                console.log('about to send new notification args = ');
                console.log(args);
                await Meteor.callAsync("galileo.notification.new", exp.user_id, msg, url, type, args);
            } else {
                return undefined;
            }
        } else {
            return undefined;
        }
    },

    "galileo.experiments.addDiscusionComment": async function (expId, user, index, message) {
        const map = await Meteor.callAsync('galileo.run.getParticipantMap', expId, user);
        const num = parseInt(index);
        const exp = await Meteor.callAsync('galileo.experiments.getExperiment', expId);
        const discussion = exp.discussion;

        const comment = {
            "author_name": map,
            "author_id": user._id,
            "create_time": new Date().toString().split(' ').splice(0, 4).join(' '),
            "post": message
        };

        discussion[num]['responses'].push(comment);

        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                discussion: discussion
            }
        });
    },

    "galileo.experiments.addDiscusionThread": async function (expId, user, message) {
        const map = await Meteor.callAsync('galileo.run.getParticipantMap', expId, user);
        const exp = await Meteor.callAsync('galileo.experiments.getExperiment', expId);

        if (exp.discussion === undefined) {
            exp.discussion = [];
        }

        const discussion = exp.discussion;
        const index = discussion.length;

        const comment = {
            "author_name": map,
            "author_id": user._id,
            "create_time": new Date().toString().split(' ').splice(0, 4).join(' '),
            "post": message,
            "index": index,
            "responses": [],
        };

        discussion.push(comment);

        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                discussion: discussion
            }
        });
    },

    'galileo.experiments.sendMorningNewEmail': async function () {
        console.log('~~~~~~~~~~~~~~~~~sendMorningNewEmail for exp');
        const now = Time.getNowInGmt().getDate().getHours() - 7;
        
        const user = await Meteor.users.find({
            "profile.is_admin": true,
            "profile.send_admin_email_time": {
                $exists: true
            }
        }, {
            "profile.send_admin_email_time": 1
        }).fetchAsync();
        
        let sendTime = 9;
        if (user && user !== undefined && user[0] && user[0].profile.send_admin_email_time) {
            sendTime = user[0].profile.send_admin_email_time;
        }

        if (sendTime === now) {
            const nowInGMT = new Time(new Date());
            const yesterdayInGMT = new Time(new Date()).addDay(-1);

            const newUsers = await Meteor.users.find({
                createdAt: {
                    $lte: nowInGMT.getDate(),
                    $gt: yesterdayInGMT.getDate()
                },
            }).fetchAsync();

            let newExperiments = await Experiments.find({
                create_date_time: {
                    $lte: nowInGMT.getDate(),
                    $gt: yesterdayInGMT.getDate()
                }
            }).fetchAsync();

            const newExperiments1 = await Experiments.find({
                create_date_time: {
                    $exists: false
                },
                status_change_date_time: {
                    $lte: nowInGMT.getDate(),
                    $gt: yesterdayInGMT.getDate()
                }
            }).fetchAsync();

            newExperiments = newExperiments.concat(newExperiments1);
            newExperiments = Array.from(new Set(newExperiments));

            const userList = [];

            for (let i = 0; i < newUsers.length; i++) {
                const user = {
                    username: newUsers[i].username,
                    id: newUsers[i]._id,
                };

                if (newUsers[i].username && newUsers[i].username != "") {
                    user.username = newUsers[i].username;
                } else {
                    user.username = "No username set";
                }
                
                if (newUsers[i].emails) {
                    user.email = newUsers[i].emails[0].address;
                } else if (newUsers[i].services && newUsers[i].services.coursera) {
                    user.email = "No email, coursera log in";
                } else if (newUsers[i].services && newUsers[i].services.google && newUsers[i].services.google.email) {
                    user.email = newUsers[i].services.google.email;
                } else if (newUsers[i].services && newUsers[i].services.facebook && newUsers[i].services.facebook.email) {
                    user.email = newUsers[i].services.facebook.email;
                } else if (newUsers[i].services && newUsers[i].services.openhumans) {
                    user.email = "No email, openhumans log in";
                } else {
                    user.email = "No Email";
                }

                if (newUsers[i].galileo && newUsers[i].galileo.country) {
                    user.country = newUsers[i].galileo.country;
                } else {
                    user.country = "No country set";
                }

                if (newUsers[i].galileo && newUsers[i].galileo.city) {
                    user.city = newUsers[i].galileo.city;
                } else {
                    user.city = "No city set";
                }

                userList.push(user);
            }

            const expList = [];

            for (let i = 0; i < newExperiments.length; i++) {
                const exp_id = newExperiments[i]._id;
                const exp = await Meteor.callAsync('galileo.experiments.getExperiment', exp_id);

                if (exp) {
                    const expToAdd = {
                        creator: exp.username,
                        id: exp_id,
                    };

                    if (exp.design && exp.design.cause && exp.design.relation && exp.design.effect) {
                        expToAdd.title = exp.design.cause + " " + exp.design.relation + " " + exp.design.effect;
                    } else {
                        expToAdd.title = "No title set";
                    }

                    if (exp.mendel_ga_id) {
                        expToAdd.mendel = exp.mendel_ga_id;
                    } else {
                        expToAdd.mendel = "No mendel set";
                    }

                    expList.push(expToAdd);
                }
            }

            const type = NotificationType.NEW_EXPS_PARTICIPANTS;

            const args = {
                newExps: expList,
                numExps: expList.length,
                newUsers: userList,
                numUsers: userList.length,
                date: dateStr(yesterdayInGMT.getDate())
            };

            await Promise.all([
                Meteor.callAsync('galileo.console.emailNotify', "otoledan@ucsd.edu", type, args),
                Meteor.callAsync('galileo.console.emailNotify', "d3gu@ucsd.edu", type, args),
                Meteor.callAsync('galileo.console.emailNotify', "gutinstinct@ucsd.edu", type, args),
                Meteor.callAsync('galileo.console.emailNotify', "srk@ucsd.edu", type, args)
            ]);

            return true;
        }
    },

    'galileo.experiments.sendWeeklyNewsEmail': async function (skipcheck, debug_target) {
        if (skipcheck === undefined) {
            skipcheck = "0";
        }

        const now = Time.getNowInGmt().getDate().getHours() - 7;
        const sendTime = 17;

        if (sendTime === now || skipcheck == "1") {
            const nowInGMT = new Time(new Date());
            const lastSundayInGMT = new Time(new Date()).addDay(-7);

            let newExperiments = await Experiments.find({
                create_date_time: {
                    $lte: nowInGMT.getDate(),
                    $gt: lastSundayInGMT.getDate()
                }
            }).fetchAsync();

            newExperiments = Array.from(new Set(newExperiments));

            if (newExperiments.length >= 0) {
                const expNeedRviewerList = [];
                const expNeedJoinList = [];

                for (let i = 0; i < newExperiments.length; i++) {
                    const exp_id = newExperiments[i]._id;
                    const exp = await Meteor.callAsync('galileo.experiments.getExperiment', exp_id);
                    
                    if (exp) {
                        const expToAdd = {};

                        expToAdd.joinLink = "https://galileo-ucsd.org/galileo/join/consent/" + exp_id;
                        
                        if (exp.design && exp.design.cause && exp.design.relation && exp.design.effect) {
                            expToAdd.title = exp.design.cause + " " + exp.design.relation + " " + exp.design.effect;
                        } else {
                            expToAdd.title = "No title set";
                        }

                        if (exp.mendel_ga_id) {
                            expToAdd.mendel = exp.mendel_ga_id;
                        } else {
                            expToAdd.mendel = "No mendel set";
                        }

                        if (exp.status >= 2 && exp.status <= 4) {
                            expToAdd.reviewLink = "https://galileo-ucsd.org/galileo/share/review/" + exp_id;
                            expNeedRviewerList.push(expToAdd);
                        } else if (exp.status >= 8 && exp.status <= 9) {
                            expNeedJoinList.push(expToAdd);
                        }
                    }
                }

                const type = NotificationType.NEW_EXPS_WEEKLY_UPDATE;
                const args = {
                    expsNeedReviewer: expNeedRviewerList,
                    expsNeedJoin: expNeedJoinList,
                    numExps: expNeedRviewerList.length + expNeedJoinList.length
                };

                if (debug_target != undefined) {
                    args.username = " 😂 Åland";
                    await Meteor.callAsync('galileo.console.emailNotify', debug_target, type, args);
                } else {
                    const allUsers = await Meteor.users.find({
                        emails: {
                            $exists: true
                        },
                    }).fetchAsync();

                    for (const user of allUsers) {
                        if (user.emails[0].address && user.emails[0].address != "") {
                            if (user.username && user.username != "") {
                                args.username = " " + user.username;
                            } else {
                                args.username = "";
                            }
                            await Meteor.callAsync('galileo.console.emailNotify', user.emails[0].address, type, args);
                        }
                    }
                }
                return true;
            }
        }
    },

    'galileo.experiments.changeStatus': async function (expId, newStatus) {
        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                status: newStatus
            }
        });

        return true;
    },

    'galileo.experiments.getExperimentsByUser': async function (targetUserID) {
        console.log("in server side galileo.experiments.getExperimentsByUser");
        return await getExperimentsByUserHelper(targetUserID);
    },

    'galileo.experiments.getExperimentByExpId': async function (exp_id) {
        const exp = await Experiments.findOneAsync({ _id: exp_id });
        if (exp) {
            return exp;
        } else {
            console.log("Error: can't find the target experiment");
        }
    },

    'galileo.experiments.getExperiments': async function (mendel) {
        let pipeline;

        if (!mendel) {
            pipeline = [
                {
                    $match: {
                        status: { $gte: ExperimentStatus.DESIGNED },
                        mendel_ga_id: { $in: ["KOMBUCHA", "KEFIR", "MICROSETTA", "DIET", "OPENHUMANS", "SOYLENT", "ATHLETES"] }
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
            ];
        } else {
            pipeline = [
                {
                    $match: {
                        status: { $gte: ExperimentStatus.DESIGNED },
                        mendel_ga_id: { $in: [mendel] }
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
            ];
        }

        return new Promise((resolve, reject) => {
            Experiments.rawCollection().aggregate(pipeline).toArray((error, result) => {
                if (error) {
                    reject(error);
                } else {
                    resolve(result);
                }
            });
        });
    },

    'galileo.experiments.copyExperimentByExpId': async function (expId, userId) {
        const user = await Meteor.users.find({ _id: userId }, { fields: { username: 1 } }).fetchAsync();
        const userObj = user[0];
        const exp = await Experiments.findOneAsync({ _id: expId });
        let designId = "";
        
        if (exp) {
            const design = await ExperimentDesigns.findOneAsync({ _id: exp.curr_design_id });
            const new_design_obj = {
                "create_date_time": new Date(),
                "username": userObj.username,
                "intuition": design.intuition,
                "cause": design.cause,
                "relation": design.relation,
                "effect": design.effect,
                "mechanism": design.mechanism,
                "related_works": design.related_works,
                "cause_measure": design.cause_measure,
                "effect_measure": design.effect_measure,
                "feedback_request": design.feedback_request,
                "criteria": design.criteria,
                "condition": design.condition,
                "timeStamp": {
                    "finishIntuition": undefined,
                    "finishMeasureCause": undefined,
                    "finishMeasureEffect": undefined,
                    "finishRemindTime": undefined,
                    "finishProvideSteps": undefined,
                    "finishProvideCriteria": undefined,
                    "finishDesign": undefined
                }
            };
            designId = await ExperimentDesigns.insertAsync(new_design_obj);
        }

        const new_exp_obj = {
            "user_id": userId,
            "username": userObj.username,
            "curr_design_id": designId,
            "versions": [{
                "create_date_time": new Date(),
                "design_id": designId
            }],
            "status": ExperimentStatus.CREATED,
            "status_change_date_time": new Date(),
            "design_progress": 7,
            "feedback_users": [],
            "pilot_users": [],
            "run_users": [],
            "waitlist_users": [],
            "flag_status": false,
            "flag_user": "",
            "flag_reason": "",
            "mendel_ga_id": exp.mendel_ga_id,
            "min_participant_count": 20,
            "clarification": [],
            "results": {
                title: "",
                graph: "",
                control: {
                    graph: ""
                },
                experimental: {
                    graph: ""
                }
            }
        };
        const exp_id = await Experiments.insertAsync(new_exp_obj);

        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "exp_id": exp_id,
            }
        });

        return {
            "expId": exp_id,
            "designId": designId
        };
    },

    'galileo.experiments.getPilotingExperiments': async function () {
        const experiments = await Experiments.find({
            status: {
                $gte: ExperimentStatus.DESIGNED,
                $lte: ExperimentStatus.OPEN_FOR_PILOT
            }
        }, {
            fields: {
                "_id": 1
            }
        }).fetchAsync();

        const results = await Promise.all(
            experiments.map(obj => Meteor.callAsync("galileo.experiments.getExperiment", obj._id))
        );

        return results;
    },

    'galileo.experiments.getExperimentAmount': async function () {
        return await Experiments.find({
            status: {
                $gte: ExperimentStatus.DESIGNED
            }
        }).countAsync();
    },

    'galileo.experiments.getStatus': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        if (exp) {
            return exp.status;
        } else {
            return undefined;
        }
    },

    'galileo.experiments.setSentThankYou': async function (expId) {
        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                sent_thank_you: true
            }
        });
    },

    'galileo.experiments.requestDataAnalysis': async function (expId) {
        const status = ExperimentStatus.ANALYSIS_REQUESTED;
        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                "status": status
            }
        });
    },

    'galileo.experiments.getMulExperimentWithParticipantData': async function (userId) {
        const exps = await getExperimentsByUserHelper(userId);
        const ongoingExps = [];
        
        exps.forEach(function (element) {
            if (element.status === ExperimentStatus.PREPARING_TO_START || element.status === ExperimentStatus.STARTED) {
                ongoingExps.push(element);
            }
        });
        
        const result = await Promise.all(
            ongoingExps.map(exp => getExperimentWithParticipantDataHelper(exp._id))
        );
        
        return result;
    },

    'galileo.experiments.getExperimentsWithReviewData': async function (userId) {
        const exps = await getExperimentsByUserHelper(userId);
        const underReviewExps = [];
        
        exps.forEach(function (element) {
            if (element.status >= ExperimentStatus.OPEN_FOR_REVIEW &&
                element.status <= ExperimentStatus.REVIEWED) {
                underReviewExps.push(element);
            }
        });
        
        const result = await Promise.all(
            underReviewExps.map(exp => getExperimentWithCommentDataHelper(exp._id))
        );
        
        return result;
    },

    'galileo.experiments.getReadyToRunExperiment': async function (userId) {
        const exps = await getExperimentsByUserHelper(userId);
        const readyToRunExps = [];
        
        exps.forEach(function (element) {
            if (element.status == ExperimentStatus.READY_TO_RUN) {
                readyToRunExps.push(element);
            }
        });
        
        return readyToRunExps;
    },

    'galileo.experiments.getExperimentWithParticipantData': async function (expId) {
        return await getExperimentWithParticipantDataHelper(expId);
    },

    'galileo.experiments.getParticipatingExpUnderReviewing': async function (userId) {
        const results = await Participations.find({
            user_id: userId,
            status: {
                $gte: ParticipationStatus.PASSED_CRITERIA
            }
        }).fetchAsync();

        if (results) {
            let returnResult = undefined;
            
            for (const result of results) {
                const exp = await Experiments.findOneAsync({
                    _id: result.exp_id
                });
                
                if (exp && exp.status >= 2 && exp.status <= 4 || exp.status === 8) {
                    const expDesign = await ExperimentDesigns.findOneAsync({
                        _id: exp.curr_design_id
                    });
                    
                    if (expDesign) {
                        exp.design = expDesign;
                        const user = await Meteor.users.find({
                            _id: exp.user_id
                        }, {
                            fields: {
                                username: 1
                            }
                        }).fetchAsync();

                        const pResult = await Participations.findOneAsync({
                            user_id: userId,
                            exp_id: exp._id
                        });
                        
                        exp.pResult = pResult;
                        returnResult = exp;
                    }
                }
            }

            return returnResult;
        } else {
            return undefined;
        }
    },

    'galileo.experiments.updateShareInfo': async function (exp_id, first, second, third) {
        const exp = await Experiments.findOneAsync({ _id: exp_id });
        const shareInfoObj = {
            "who are you": first,
            "what world would learn": second,
            "expected time": third
        };
        
        if (exp) {
            exp.shareInfo = shareInfoObj;
            await Experiments.updateAsync({ _id: exp._id }, { $set: exp });
        }
    },

    'galileo.experiments.getParticipatingExpByUser': async function (userId) {
        const results = await Participations.find({
            user_id: userId,
            status: {
                $gte: ParticipationStatus.PREPARING,
                $lt: ParticipationStatus.WAITLIST
            }
        }).fetchAsync();

        if (results) {
            let returnResult = undefined;
            
            for (const result of results) {
                const exp = await Experiments.findOneAsync({
                    _id: result.exp_id
                });
                
                if (exp && exp.status >= 9 && exp.status <= 10) {
                    const expDesign = await ExperimentDesigns.findOneAsync({
                        _id: exp.curr_design_id
                    });
                    
                    if (expDesign) {
                        exp.design = expDesign;
                        const user = await Meteor.users.find({
                            _id: exp.user_id
                        }, {
                            fields: {
                                username: 1
                            }
                        }).fetchAsync();

                        if (exp.run_users.length > 0) {
                            const userDataTemp = await Meteor.users.find({
                                _id: userId
                            }, {
                                fields: {
                                    'username': 1
                                }
                            }).fetchAsync();
                            
                            const userData = userDataTemp[0];
                            userData.duration = exp.duration;
                            userData.all_cause_data = [];
                            userData.all_effect_data = [];
                            userData.all_cause_data = result.cause_data;
                            userData.all_effect_data = result.effect_data;
                            userData.status = result.status;
                            userData.group = result.group;

                            exp.participantInfoResults = userData;
                        }

                        const pResult = await Participations.findOneAsync({
                            user_id: userId,
                            exp_id: exp._id
                        });
                        
                        exp.pResult = pResult;
                        returnResult = exp;
                    }
                }
            }

            return returnResult;
        } else {
            return undefined;
        }
    },

    'galileo.experiments.getParticipatingExpByUserComplete': async function (userId) {
        const results = await Participations.find({
            user_id: userId,
            status: 5
        }).fetchAsync();

        if (results) {
            const returnResult = [];
            
            for (const result of results) {
                const exp = await Experiments.findOneAsync({
                    _id: result.exp_id
                });
                
                if (exp && exp.status >= 11) {
                    const expDesign = await ExperimentDesigns.findOneAsync({
                        _id: exp.curr_design_id
                    });
                    
                    if (expDesign) {
                        exp.design = expDesign;
                        const user = await Meteor.users.find({
                            _id: exp.user_id
                        }, {
                            fields: {
                                username: 1
                            }
                        }).fetchAsync();

                        if (exp.run_users.length > 0) {
                            const userDataTemp = await Meteor.users.find({
                                _id: userId
                            }, {
                                fields: {
                                    'username': 1
                                }
                            }).fetchAsync();
                            
                            const userData = userDataTemp[0];
                            userData.duration = exp.duration;
                            userData.all_cause_data = [];
                            userData.all_effect_data = [];
                            userData.all_cause_data = result.cause_data;
                            userData.all_effect_data = result.effect_data;
                            userData.status = result.status;
                            userData.group = result.group;

                            exp.participantInfoResults = userData;
                        }

                        const pResult = await Participations.findOneAsync({
                            user_id: userId,
                            exp_id: exp._id
                        });
                        
                        exp.pResult = pResult;
                        returnResult.push(exp);
                    }
                }
            }
            
            return returnResult;
        } else {
            return undefined;
        }
    },

    'galileo.experiments.getParticipatingExpByUserExp': async function (userId, expId) {
        const results = await Participations.find({
            user_id: userId,
            exp_id: expId
        }).fetchAsync();

        if (results) {
            let returnResult = undefined;
            
            for (const result of results) {
                const exp = await Experiments.findOneAsync({
                    _id: result.exp_id
                });
                
                if (exp && exp.status >= 9 && exp.status <= 13) {
                    const expDesign = await ExperimentDesigns.findOneAsync({
                        _id: exp.curr_design_id
                    });
                    
                    if (expDesign) {
                        exp.design = expDesign;
                        const user = await Meteor.users.find({
                            _id: exp.user_id
                        }, {
                            fields: {
                                username: 1
                            }
                        }).fetchAsync();

                        if (exp.run_users.length > 0) {
                            const userDataTemp = await Meteor.users.find({
                                _id: userId
                            }, {
                                fields: {
                                    'username': 1
                                }
                            }).fetchAsync();
                            
                            const userData = userDataTemp[0];
                            userData.duration = exp.duration;
                            userData.all_cause_data = [];
                            userData.all_effect_data = [];
                            userData.all_cause_data = result.cause_data;
                            userData.all_effect_data = result.effect_data;
                            userData.group = result.group;

                            exp.participantInfoResults = userData;
                        }

                        const pResult = await Participations.findOneAsync({
                            user_id: userId,
                            exp_id: exp._id
                        });
                        
                        exp.pResult = pResult;
                        returnResult = exp;
                    }
                }
            }

            return returnResult;
        } else {
            return undefined;
        }
    },

    'galileo.experiments.stopParticipating': async function (userId, expId, content) {
        console.log("in galileo.experiments.stopParticipating~~~");
        const result = await Participations.findOneAsync({
            user_id: userId,
            exp_id: expId
        });
        
        const partMap = result.participantMap;
        result.stop_reason = content;
        result.status = ParticipationStatus.DROPPED;
        await Participations.updateAsync({ _id: result._id }, { $set: result });

        const exp = await Experiments.find({ _id: expId }, { fields: { run_users: 1 } }).fetchAsync();
        const expObj = exp[0];
        const index = expObj.run_users.indexOf(partMap);
        if (index > -1) {
            expObj.run_users.splice(index, 1);
            console.log("removed " + userId + " from exp " + expId);
        }
        await Experiments.updateAsync({ _id: expObj._id }, { $set: expObj });
    },

    'galileo.experiments.addCauseData': async function (userId, expId, currentDay, content) {
        const result = await Participations.findOneAsync({
            user_id: userId,
            exp_id: expId
        });

        result.cause_data[parseInt(currentDay)].status = 2;
        result.cause_data[parseInt(currentDay)].value = content;
        result.cause_data[parseInt(currentDay)].complete_time = new Date();
        result.cause_data[parseInt(currentDay)].start_time = result.cause_data[parseInt(currentDay)].start_time;
        result.cause_data[parseInt(currentDay)].compliance = result.cause_data[parseInt(currentDay)].compliance;

        await Participations.updateAsync({
            _id: result._id
        }, {
            $set: result
        });
    },

    'galileo.experiments.addEffectData': async function (userId, expId, currentDay, content) {
        const result = await Participations.findOneAsync({
            user_id: userId,
            exp_id: expId
        });

        result.effect_data[parseInt(currentDay)].status = 2;
        result.effect_data[parseInt(currentDay)].value = content;
        result.effect_data[parseInt(currentDay)].complete_time = new Date();
        result.effect_data[parseInt(currentDay)].start_time = result.effect_data[parseInt(currentDay)].start_time;
        result.effect_data[parseInt(currentDay)].compliance = result.effect_data[parseInt(currentDay)].compliance;

        await Participations.updateAsync({
            _id: result._id
        }, {
            $set: result
        });
    },

    'galileo.experiments.addClarification': async function (userId, expId, content, index) {
        let obj = {};
        const part = await Participations.find({
            user_id: userId
        }, {
            fields: {
                participantMap: 1
            }
        }).fetchAsync();
        
        const exp = await Experiments.find({
            _id: expId
        }, {
            fields: {
                user_id: 1,
                username: 1,
                clarification: 1
            }
        }).fetchAsync();

        const partObj = part[0];
        const expObj = exp[0];

        if (userId !== expObj.user_id) {
            obj["clarification." + index] = {
                "author_name": partObj.participantMap,
                "author_id": userId,
                "create_time": new Date().toString().split(' ').splice(0, 4).join(' '),
                "resolved": false,
                "question": content,
                "index": index
            };
            await Experiments.updateAsync(expId, {
                $set: obj
            });
        } else if (userId === expObj.user_id) {
            obj["clarification." + index] = {
                "author_name": expObj.clarification[index].author_name,
                "author_id": expObj.clarification[index].author_id,
                "create_time": expObj.clarification[index].create_time,
                "resolved": true,
                "question": expObj.clarification[index].question,
                "index": expObj.clarification[index].index,
                "answer": content,
                "resolve_time": new Date().toString().split(' ').splice(0, 4).join(' '),
                "creator": expObj.username
            };
            await Experiments.updateAsync(expId, {
                $set: obj
            });
        }
    },

    'galileo.experiments.getExperimentsByDate': async function (start, end) {
        const exps = await Experiments.find({
            start_date_time: {
                $gte: start,
                $lt: end
            }
        }).fetchAsync();

        for (let i = 0; i < exps.length; i++) {
            const expDesign = await ExperimentDesigns.findOneAsync({
                _id: exps[i].curr_design_id
            });
            exps[i].design = expDesign;
        }
        return exps;
    },

    'galileo.experiments.getExperimentsPreparingToStart': async function () {
        const exps = await Experiments.find({
            status: ExperimentStatus.PREPARING_TO_START
        }).fetchAsync();

        for (let i = 0; i < exps.length; i++) {
            const expDesign = await ExperimentDesigns.findOneAsync({
                _id: exps[i].curr_design_id
            });
            exps[i].design = expDesign;

            const user = await Meteor.users.find({
                _id: exps[i].user_id
            }).fetchAsync();

            exps[i].timezone = ExperimentHelper.getTimezoneOffset(user[0]);
        }
        return exps;
    },

    'galileo.experiments.getExperiment': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        if (exp) {
            const expDesign = await ExperimentDesigns.findOneAsync({
                _id: exp.curr_design_id
            });
            
            if (expDesign) {
                exp.design = expDesign;
                const user = await Meteor.users.find({
                    _id: exp.user_id
                }, {
                    fields: {
                        username: 1
                    }
                }).fetchAsync();

                if (user && user[0] && user[0].username) {
                    exp.username = user[0].username;
                }

                return exp;
            } else {
                return undefined;
            }
        } else {
            throw new Meteor.Error("Experiment does not exist");
        }
    },

    'galileo.experiments.setMinParticipantCount': async function (expId, newCount) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        if (exp) {
            await Experiments.updateAsync(expId, {
                $set: {
                    min_participant_count: newCount
                }
            });
            return true;
        } else {
            return undefined;
        }
    },

    'galileo.experiments.getSingleMendelExpNum': async function (mendel) {
        return await Experiments.find({
            mendel_ga_id: mendel,
            status: {
                $gte: ExperimentStatus.DESIGNED
            }
        }).countAsync();
    },

    'galileo.experiments.getMendelExpNum': async function (mendelIdArray) {
        const res = {};

        await Promise.all(mendelIdArray.map(async (id) => {
            res[id] = await Meteor.callAsync("galileo.experiments.getSingleMendelExpNum", id);
        }));

        return res;
    },

    'galileo.experiments.getSingleMendelUserNum': async function (mendel) {
        return new Promise((resolve, reject) => {
            Experiments.rawCollection().distinct("user_id", {
                mendel_ga_id: mendel,
                status: {
                    $gte: ExperimentStatus.DESIGNED
                }
            }, (error, result) => {
                if (error) {
                    reject(error);
                } else {
                    resolve(result.length);
                }
            });
        });
    },

    'galileo.experiments.getMendelUserNum': async function (mendelIdArray) {
        const res = {};

        await Promise.all(mendelIdArray.map(async (id) => {
            res[id] = await Meteor.callAsync("galileo.experiments.getSingleMendelUserNum", id);
        }));

        return res;
    },

    'galileo.experiments.getExperimentStats': async function (expId) {
        const res = {};
        res.reviewerCount = -1;
        res.pilotCount = -1;
        res.participantCount = -1;

        const [reviewerCount, pilotCount, participantCount] = await Promise.all([
            Feedbacks.find({ "exp_id": expId }).countAsync(),
            Pilots.find({ "exp_id": expId }).countAsync(),
            Participations.find({ "exp_id": expId }).countAsync()
        ]);

        res.reviewerCount = reviewerCount;
        res.pilotCount = pilotCount;
        res.participantCount = participantCount;

        return res;
    },

    'galileo.experiments.getMeasures': async function (expId) {
        const result = await ExperimentDesigns.find({
            exp_id: expId
        }, {
            fields: {
                cause_measure: 1,
                effect_measure: 1
            }
        }).fetchAsync();

        if (result && result.length > 0 && result[0]) {
            return result[0];
        } else {
            throw new Meteor.Error("Experiment with id - " + expId + " not found");
        }
    },

    'galileo.experiments.getMendelId': async function (expId) {
        const result = await Experiments.find({
            _id: expId
        }, {
            fields: {
                mendel_ga_id: 1
            }
        }).fetchAsync();

        if (result && result.length > 0 && result[0] && result[0].mendel_ga_id) {
            return result[0].mendel_ga_id;
        } else {
            return "";
        }
    },

    'galileo.experiments.getOpenHumansSources': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        const designId = exp.curr_design_id;
        const result = await ExperimentDesigns.find({
            _id: designId
        }, {
            fields: {
                cause_measure: 1,
                effect_measure: 1,
                open_humans_client_id: 1
            },
        }).fetchAsync();

        if (result && result.length > 0 && result[0]) {
            const res = result[0];
            const causeDataIds = res.cause_measure && res.cause_measure.ohDataSourceIds;
            const effectDataIds = res.effect_measure && res.effect_measure.ohDataSourceIds;
            const uniqueIds = [...new Set([...causeDataIds, ...effectDataIds])];
            uniqueIds.shift(); // this removes the 1st item from the array, which is 0, which is the default data source - Gut instinct sms
            return {
                dataSourceIds: uniqueIds,
                clientId: res.open_humans_client_id
            };
        } else {
            throw new Meteor.Error("Experiment with id - " + expId + " not found");
        }
    },

    'galileo.experiments.hasExperiment': async function (expId) {
        const count = await Experiments.find({
            _id: expId
        }).countAsync();
        return count === 1;
    },

    'galileo.experiments.reportAbuse': async function (expId, reportReason) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        if (exp) {
            const user = await Meteor.userAsync();
            await Experiments.updateAsync(expId, {
                $set: {
                    flag_status: true,
                    flag_user: user.username,
                    flag_reason: reportReason
                }
            });
            return true;
        } else {
            return undefined;
        }
    },

    'galileo.experiments.unreportAbuse': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        if (exp) {
            await Experiments.updateAsync(expId, {
                $set: {
                    flag_status: false,
                    flag_user: ""
                }
            });
            return true;
        } else {
            return undefined;
        }
    },

    'galileo.experiments.getHypothesis': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        if (exp) {
            const d = await ExperimentDesigns.findOneAsync({
                _id: exp.curr_design_id
            });
            
            if (d) {
                return d.cause + " " + d.relation + " " + d.effect;
            } else {
                return undefined;
            }
        }
    },

    'galileo.experiments.isCreator': async function (expId) {
        const exp = await Experiments.find({
            _id: expId
        }, {
            fields: {
                user_id: 1
            }
        }).fetchAsync();

        if (!exp || exp.length === 0) {
            return false;
        }
        return exp[0].user_id === Meteor.userId();
    },

    'galileo.experiments.isOpenForRun': async function (expId) {
        const exp = await Experiments.find({
            _id: expId
        }, {
            fields: {
                status: 1
            }
        }).fetchAsync();
        
        return exp[0].status < ExperimentStatus.STARTED;
    },

    'galileo.experiments.canRun': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        switch (exp.status) {
            case ExperimentStatus.CREATED:
            case ExperimentStatus.OPEN_FOR_PILOT:
            case ExperimentStatus.PILOT_ONGOING:
            case ExperimentStatus.PREPARING_TO_START:
            case ExperimentStatus.STARTED:
            case ExperimentStatus.FINISHED:
                return false;
            default:
                return true;
        }
    },

    'galileo.experiments.hasEnded': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        return (exp.status === ExperimentStatus.FINISHED);
    },

    'galileo.experiments.getCurrentUserRole': async function (expId) {
        const role = {
            isCreator: false,
            isReviewer: false,
            isPilotUser: false,
            isParticipant: false,
            isFailedCriteria: false,
            isWaitlist: false
        };

        const exp = await Experiments.find({
            _id: expId
        }, {
            fields: {
                user_id: 1,
                feedback_users: 1
            }
        }).fetchAsync();

        const curUserId = Meteor.userId();
        const currUser = await Meteor.users.find({
            _id: curUserId
        }, {
            fields: {
                'galileo.feedback_experiments': 1
            }
        }).fetchAsync();

        if (!exp || exp.length === 0) {
            return role;
        }

        const expObj = exp[0];
        const feedback_exps = currUser[0].galileo.feedback_experiments;

        if (await Meteor.callAsync("galileo.run.isFailedCriteria", expId)) {
            role.isFailedCriteria = true;
        }

        if (expObj.user_id === curUserId) {
            role.isCreator = true;
            return role;
        }

        for (const feedbackExp of feedback_exps) {
            if (feedbackExp === expId) {
                role.isReviewer = true;
                return role;
            }
        }

        if (await Meteor.callAsync("galileo.pilot.isPilot", expId)) {
            role.isPilotUser = true;
            return role;
        }
        
        if (await Meteor.callAsync("galileo.run.isWaitlisting", expId)) {
            role.isWaitlist = true;
            return role;
        }

        if (await Meteor.callAsync("galileo.run.isParticipant", expId)) {
            role.isParticipant = true;
            return role;
        }

        return role;
    },

    'galileo.experiments.create': async function (intuition, username, mendel) {
        const design = generateDesignObject(intuition, username);
        const designId = await ExperimentDesigns.insertAsync(design);

        const exp = generateExperimentObject(Meteor.userId(), username, designId, mendel);
        const expId = await Experiments.insertAsync(exp);

        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "exp_id": expId,
            }
        });

        return {
            "expId": expId,
            "designId": designId
        };
    },

    'galileo.experiments.getDesignProgress': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        return exp.design_progress;
    },

    'galileo.experiments.setDesignProgress': async function (expId, progress) {
        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                "design_progress": progress
            }
        });
    },

    'galileo.experiments.getShuffledCriteria': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        const designId = exp.curr_design_id;
        const design = await ExperimentDesigns.findOneAsync({
            _id: designId
        });
        
        const criteria = design.criteria;

        const arr = [];
        for (const i in criteria.inclusion) arr.push(criteria.inclusion[i]);
        for (const i in criteria.exclusion) arr.push(criteria.exclusion[i]);

        for (let i = 0; i < arr.length; i++) {
            const swapId = Math.floor(Math.random() * (arr.length - i)) + i;
            const temp = arr[swapId];
            arr[swapId] = arr[i];
            arr[i] = temp;
        }
        return arr;
    },

    'galileo.experiments.getUnshuffledInclusionCriteria': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        const designId = exp.curr_design_id;
        const design = await ExperimentDesigns.findOneAsync({
            _id: designId
        });
        
        const criteria = design.criteria;
        const arr = [];
        for (const i in criteria.inclusion) arr.push(criteria.inclusion[i]);

        return arr;
    },

    'galileo.experiments.getUnshuffledExclusionCriteria': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        });
        
        const designId = exp.curr_design_id;
        const design = await ExperimentDesigns.findOneAsync({
            _id: designId
        });
        
        const criteria = design.criteria;
        const arr = [];
        for (const i in criteria.exclusion) arr.push(criteria.exclusion[i]);

        return arr;
    },

    'galileo.experiments.setDesignedOrOpenForReview': async function (expId) {
        const finished = await Meteor.callAsync("galileo.profile.hasFinishedEthics");
        
        let status = ExperimentStatus.DESIGNED;
        if (finished) {
            status = ExperimentStatus.OPEN_FOR_REVIEW;
        }
        
        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                "status": status,
                "create_date_time": new Date(),
                "status_change_date_time": new Date()
            }
        });
    },

    'galileo.experiments.setDesigned': async function (expId) {
        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                "status": ExperimentStatus.DESIGNED,
                "create_date_time": new Date(),
                "status_change_date_time": new Date()
            }
        });
    },

    'galileo.experiments.setOpenForPilot': async function (expId) {
        if (await Meteor.callAsync("galileo.experiments.isCreator", expId)) {
            await Experiments.updateAsync({
                _id: expId
            }, {
                $set: {
                    "status": ExperimentStatus.OPEN_FOR_PILOT,
                    "status_change_date_time": new Date()
                }
            });
        } else {
            throw new Meteor.Error("you are not creator of the experiment");
        }
    },

    'galileo.experiments.setPiloting': async function (expId) {
        await Experiments.updateAsync({
            _id: expId
        }, {
            $set: {
                "status": ExperimentStatus.PILOT_ONGOING,
                "status_change_date_time": new Date()
            }
        });
    },

    'galileo.experiments.version.updateVersionIfNeeded': async function (expId) {
        const exp = await Experiments.findOneAsync({
            _id: expId
        }, {
            fields: {
                curr_design_id: 1,
                versions: 1,
                status: 1
            }
        });

        if (!exp.status || exp.status < ExperimentStatus.DESIGNED) {
            return exp.curr_design_id;
        }

        if (exp.versions.length > 1) {
            return exp.curr_design_id;
        }

        const currentDesign = await ExperimentDesigns.findOneAsync({
            _id: exp.curr_design_id
        });
        
        const newDesign = { ...currentDesign };
        delete newDesign["_id"];
        delete newDesign["create_date_time"];
        newDesign["update_date_time"] = new Date();

        const newDesignId = await ExperimentDesigns.insertAsync(newDesign);

        await Experiments.updateAsync({
            _id: expId
        }, {
            $push: {
                "versions": {
                    "update_date_time": new Date(),
                    "design_id": newDesignId
                }
            },
            $set: {
                "curr_design_id": newDesignId
            }
        });

        return newDesignId;
    },

    'galileo.experiments.edit.updateHypothesis': async function (expId, cause, relation, effect, mechanism, related_works) {
        const designId = await Meteor.callAsync('galileo.experiments.version.updateVersionIfNeeded', expId);
        await Meteor.callAsync('galileo.experiments.design.setHypothesis', designId, cause, relation, effect, mechanism, related_works);
    },

    'galileo.experiments.edit.updateCauseMeasure': async function (expId, reminderTime, reminderText, type, unit) {
        const designId = await Meteor.callAsync('galileo.experiments.version.updateVersionIfNeeded', expId);

        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "update_date_time": new Date(),
                "cause_measure.time": reminderTime,
                "cause_measure.reminderText": reminderText,
                "cause_measure.type": type,
                "cause_measure.unit": unit
            }
        });
    },

    'galileo.experiments.edit.updateEffectMeasure': async function (expId, reminderTime, reminderText, type, unit, minRating, maxRating) {
        const designId = await Meteor.callAsync('galileo.experiments.version.updateVersionIfNeeded', expId);

        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "update_date_time": new Date(),
                "effect_measure.time": reminderTime,
                "effect_measure.reminderText": reminderText,
                "effect_measure.type": type,
                "effect_measure.unit": unit,
                "effect_measure.minRating": minRating,
                "effect_measure.maxRating": maxRating
            }
        });
    },

    'galileo.experiments.edit.updateOpenHumansDataSources': async function (expId, causeOhIds, effectOhIds) {
        const designId = await Meteor.callAsync('galileo.experiments.version.updateVersionIfNeeded', expId);

        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "update_date_time": new Date(),
                "cause_measure.ohDataSourceIds": causeOhIds,
                "effect_measure.ohDataSourceIds": effectOhIds
            }
        });
    },

    'galileo.experiments.edit.updateExclusionCriteria': async function (expId, ec) {
        const designId = await Meteor.callAsync('galileo.experiments.version.updateVersionIfNeeded', expId);
        await Meteor.callAsync('galileo.experiments.design.setExclusionCriteria', designId, ec);
    },

    'galileo.experiments.edit.updateInclusionCriteria': async function (expId, ic) {
        const designId = await Meteor.callAsync('galileo.experiments.version.updateVersionIfNeeded', expId);
        await Meteor.callAsync('galileo.experiments.design.setInclusionCriteria', designId, ic);
    },

    'galileo.experiments.edit.updateConditionInstructions': async function (expId, design) {
        const designId = await Meteor.callAsync('galileo.experiments.version.updateVersionIfNeeded', expId);
        const controlDesc = design.condition.control.description;
        const controlSteps = design.condition.control.steps;
        const controlPrepSteps = design.condition.control.prep_steps;
        const expDesc = design.condition.experimental.description;
        const expSteps = design.condition.experimental.steps;
        const expPrepSteps = design.condition.experimental.prep_steps;
        await Meteor.callAsync('galileo.experiments.design.setConditionInstructions', designId, controlDesc, controlSteps, expDesc, expSteps, expPrepSteps, controlPrepSteps);
    },

    'galileo.experiments.checkIncompleteExp': async function () {
        console.log('~~~~~~~~~~~~~~~~~checkIncompleteExp');

        const userMap = {};
        const nowInGMT = Time.getNowInGmt();
        const nowMinus3Days = (new Time(nowInGMT)).addDay(-3);
        const nowMinus4Days = (new Time(nowInGMT)).addDay(-4);
        
        console.log('nowMinus4Days = ' + nowMinus4Days.getDate());
        console.log('nowMinus3Days = ' + nowMinus3Days.getDate());

        const incompleteExps = await Experiments.find({
            status: ExperimentStatus.CREATED,
            status_change_date_time: {
                $gt: nowMinus4Days.getDate(),
                $lte: nowMinus3Days.getDate()
            }
        }).fetchAsync();

        for (const exp of incompleteExps) {
            if (userMap[exp.user_id] === undefined) {
                console.log('sending email to ' + exp.username);

                userMap[exp.user_id] = exp.user_id;

                const design = await ExperimentDesigns.findOneAsync({
                    _id: exp.curr_design_id
                });
                
                const expTitle = "Does " + design.cause + " affect " + design.effect + "?";
                const args = {
                    creatorName: exp.username,
                    expTitle: expTitle,
                    design_progress: exp.design_progress,
                    cause: design.cause
                };
                const message = "You have partially designed experiments waiting for completion";
                const url = "/galileo/me/unfinished_experiments";

                await Meteor.callAsync("galileo.notification.new", exp.user_id, message, url, NotificationType.INCOMPLETE_EXP_3DAYS, args);
            }
        }
    },

    'galileo.experiments.getFeedbackUsers': async function (expId) {
        const exp = await Experiments.find({
            _id: expId
        }, {
            fields: {
                feedback_users: 1
            }
        }).fetchAsync();
        
        const reviewers = [];
        if (exp && exp.length > 0) {
            const result = exp[0].feedback_users;
            
            for (const element of result) {
                const user = await Meteor.users.find({
                    _id: element
                }, {
                    fields: {
                        username: 1
                    }
                }).fetchAsync();
                
                reviewers.push(user[0].username);
            }
        }
        return reviewers;
    },

    'galileo.experiments.design.get': async function (designId) {
        return await ExperimentDesigns.findOneAsync({
            _id: designId
        });
    },

    'galileo.experiments.design.setTimeStamp': async function (designId, type) {
        const updateObj = {
            [`timeStamp.${type}`]: new Date()
        };

        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: updateObj
        });
    },

    'galileo.experiments.design.setIntuition': async function (designId, intuition) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "intuition": intuition
            }
        });
    },

    'galileo.experiments.design.setHypothesis': async function (designId, cause, relation, effect, mechanism = null, related_works = null) {
        const data = {
            "update_date_time": new Date(),
            "cause": cause,
            "relation": relation,
            "effect": effect,
        };

        if (mechanism != null) {
            data.mechanism = mechanism;
        }

        if (related_works != null) {
            data.related_works = related_works;
        }

        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: data
        });
    },

    'galileo.experiments.design.setCause': async function (designId, cause) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "cause": cause
            }
        });
    },

    'galileo.experiments.design.setRelation': async function (designId, relation) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "relation": relation
            }
        });
    },

    'galileo.experiments.design.setEffect': async function (designId, effect) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "effect": effect
            }
        });
    },

    'galileo.experiments.design.setFeedbackRequest': async function (designId, feedbackRequest) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "update_date_time": new Date(),
                "feedback_request": feedbackRequest
            }
        });
    },

    'galileo.experiments.design.setFollowupMessage': async function (designId, followupMessageCause, followupMessageEffect) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "followup_message_cause": followupMessageCause,
                "followup_message_effect": followupMessageEffect,
            }
        });
    },

    'galileo.experiments.design.setMechanism': async function (designId, mechanism) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "mechanism": mechanism
            }
        });
    },

    'galileo.experiments.design.setVariableIdentified': async function (designId) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "variables_identified": true
            }
        });
    },

    'galileo.experiments.design.setCauseMeasure': async function (designId, causeMeasure) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "cause_measure": causeMeasure
            }
        });
    },

    'galileo.experiments.design.setEffectMeasure': async function (designId, effectMeasure) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "effect_measure": effectMeasure
            }
        });
    },

    'galileo.experiments.design.setInclusionCriteria': async function (designId, inclusionCriteria) {
        const ic = [];
        inclusionCriteria.forEach(function (elt) {
            if (elt.substring(0, 3).toLowerCase() === 'you') {
                const length = elt.length + 1;
                const validString = elt.substring(3, length);
                ic.push(validString);
            } else {
                ic.push(elt);
            }
        });
        
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "update_date_time": new Date(),
                "criteria.inclusion": ic
            }
        });
    },

    'galileo.experiments.design.setExclusionCriteria': async function (designId, exclusionCriteria) {
        const ec = [];
        exclusionCriteria.forEach(function (elt) {
            if (elt.substring(0, 3).toLowerCase() === 'you') {
                const length = elt.length + 1;
                const validString = elt.substring(3, length);
                ec.push(validString);
            } else {
                ec.push(elt);
            }
        });
        
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "update_date_time": new Date(),
                "criteria.exclusion": ec
            }
        });
    },

    'galileo.experiments.design.setConditionInstructions': async function (designId, control, controlGroupInstructions, experimental, expGroupInstructions, expGroupPrepInstructions, controlGroupPrepInstructions) {
        await ExperimentDesigns.updateAsync({
            _id: designId
        }, {
            $set: {
                "update_date_time": new Date(),
                "condition": {
                    "control": {
                        "description": control,
                        "steps": controlGroupInstructions,
                        "prep_steps": controlGroupPrepInstructions,
                    },
                    "experimental": {
                        "description": experimental,
                        "steps": expGroupInstructions,
                        "prep_steps": expGroupPrepInstructions,
                    }
                }
            }
        });
    },

    'galileo.experiments.analysis.printSingleCause': async function (post_data) {
        const result = await HTTP.callAsync("post", getAPIURL(Meteor.settings.analysisScriptAPI, "printSingleCause"), {
            data: post_data
        });

        const filecontent = JSON.parse(result.content)["content"];
        console.log(filecontent);
        return filecontent;
    },

    'galileo.experiments.analysis.printGreaterEffect': async function (post_data) {
        const result = await HTTP.callAsync("post", getAPIURL(Meteor.settings.analysisScriptAPI, "printGreaterEffect"), {
            data: post_data
        });

        const filecontent = JSON.parse(result.content)["content"];
        const results = filecontent.split("$$");
        results[1] = Meteor.settings.analysisImageURL + results[1];
        return "" + results[0] + "$$" + results[1];
    },
});

function getAPIURL(base, action) {
    return base + action;
}

function generateExperimentObject(userId, userName, designId, mendel) {
    return {
        "user_id": userId,
        "username": userName,
        "curr_design_id": designId,
        "versions": [{
            "create_date_time": new Date(),
            "design_id": designId
        }],
        "status": ExperimentStatus.CREATED,
        "status_change_date_time": new Date(),
        "design_progress": 0,
        "feedback_users": [],
        "pilot_users": [],
        "run_users": [],
        "waitlist_users": [],
        "flag_status": false,
        "flag_user": "",
        "flag_reason": "",
        "mendel_ga_id": mendel,
        "min_participant_count": 20,
        "clarification": [],
        "results": {
            title: "",
            graph: "",
            control: {
                graph: ""
            },
            experimental: {
                graph: ""
            }
        }
    };
}

function generateDesignObject(intuition, username) {
    return {
        "create_date_time": new Date(),
        "username": username,
        "intuition": intuition,
        "cause": undefined,
        "relation": undefined,
        "effect": undefined,
        "mechanism": undefined,
        "related_works": undefined,
        "cause_measure": {
            "type": undefined,
            "frequency": undefined,
            "time": undefined
        },
        "effect_measure": {
            "type": undefined,
            "frequency": undefined,
            "time": undefined
        },
        "feedback_request": undefined,
        "criteria": {
            "inclusion": [],
            "exclusion": []
        },
        "condition": {
            "control": {
                "description": undefined,
                "steps": []
            },
            "experimental": {
                "description": undefined,
                "steps": []
            }
        },
        "timeStamp": {
            "finishIntuition": undefined,
            "finishMeasureCause": undefined,
            "finishMeasureEffect": undefined,
            "finishRemindTime": undefined,
            "finishProvideSteps": undefined,
            "finishProvideCriteria": undefined,
            "finishDesign": undefined
        }
    };
}

async function getExperimentWithParticipantDataHelper(expId) {
    const expParticipantsData = await Participations.find({
        exp_id: expId
    }).fetchAsync();
    
    const exp = await Experiments.findOneAsync({
        _id: expId
    });
    
    if (exp) {
        const expDesign = await ExperimentDesigns.findOneAsync({
            _id: exp.curr_design_id
        });
        
        if (expDesign) {
            exp.design = expDesign;
            const user = await Meteor.users.find({
                _id: exp.user_id
            }, {
                fields: {
                    username: 1
                }
            }).fetchAsync();

            if (exp.run_users.length > 0) {
                const participantInfoResults = [];
                
                for (const currentUser of exp.run_users) {
                    const user_id = await Meteor.callAsync('galileo.run.getParticipantMapToUser', expId, currentUser);
                    const userDataTemp = await Meteor.users.find({
                        _id: user_id
                    }, {
                        fields: {
                            'username': 1,
                            'galileo.city': 1,
                            'galileo.country': 1,
                            'galileo.phone': 1,
                            'galileo.timezone': 1
                        }
                    }).fetchAsync();

                    const userData = userDataTemp[0];
                    
                    // Set flag based on country
                    const countryFlags = {
                        "USA": "flag-icon-us",
                        "CHN": "flag-icon-cn",
                        "MNE": "flag-icon-me",
                        "BRA": "flag-icon-br",
                        "NZL": "flag-icon-nz",
                        "CAN": "flag-icon-ca",
                        "GBR": "flag-icon-gb",
                        "IND": "flag-icon-in",
                        "EGY": "flag-icon-eg",
                        "AUS": "flag-icon-au",
                        "ESP": "flag-icon-es",
                        "NLD": "flag-icon-nl",
                        "DNK": "flag-icon-dk",
                        "ITA": "flag-icon-it"
                    };
                    
                    userData.flag = countryFlags[userData.galileo.country] || "flag-icon-aw";
                    userData.duration = exp.duration;
                    userData.all_cause_data = [];
                    userData.all_effect_data = [];
                    userData.participantMap = currentUser;
                    userData.user_start_date = "";

                    expParticipantsData.forEach(function (currentRecord) {
                        if (currentRecord.user_id === user_id) {
                            userData.all_cause_data = currentRecord.cause_data;
                            userData.all_effect_data = currentRecord.effect_data;
                            userData.user_start_date = currentRecord.user_startDate_inGmt;
                            userData.group = currentRecord.group;
                        }
                    });

                    participantInfoResults.push(userData);
                }
                
                exp.participantInfoResults = participantInfoResults;
            }

            if (user && user[0] && user[0].username) {
                exp.username = user[0].username;
            }

            return exp;
        } else {
            return undefined;
        }
    } else {
        return undefined;
    }
}

async function getExperimentWithCommentDataHelper(expId) {
    const expFeedbacksData = await Feedbacks.find({
        exp_id: expId
    }).fetchAsync();
    
    const exp = await Experiments.findOneAsync({
        _id: expId
    });
    
    if (exp) {
        const expDesign = await ExperimentDesigns.findOneAsync({
            _id: exp.curr_design_id
        });
        
        if (expDesign) {
            exp.design = expDesign;
            exp.expFeedbacksData = expFeedbacksData;
        }

        return exp;
    } else {
        return undefined;
    }
}

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

function dateStr(date) {
    return dayWeekStr(date.getDay()) + ", " + monthStr(date.getMonth()) + ". " + date.getDate() + ", " + date.getFullYear();
}

function monthStr(month) {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return months[month];
}

function dayWeekStr(day) {
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    return days[day];
}