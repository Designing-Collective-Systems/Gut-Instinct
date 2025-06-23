# iron:router
## imports/api/routes.js, clients/templates/gallelio/question/_.js, clients/templates/visualization/mainfile.js --> changed all of these from iron:router to flowrouter

# Modernizing Async Operations

## Problem
The original codebase used Meteor's legacy synchronous database APIs and callback-based patterns that were deprecated and removed in Meteor 3.0+. These blocking operations caused performance issues and are incompatible with Meteor 3.2's fiber-free, async-first architecture.

## Solution Overview
Migrated the entire codebase to use Meteor 3.2's modern async/await APIs and Promise-based patterns for improved performance and compatibility.

## Key Changes Made

### 1. Database Operations
- **Before**: `Collection.findOne()`, `Collection.find().fetch()`, `Collection.update()`, `Collection.insert()`
- **After**: `Collection.findOneAsync()`, `Collection.find().fetchAsync()`, `Collection.updateAsync()`, `Collection.insertAsync()`

### 2. Method Definitions
- **Before**: `'methodName': function() { ... }`
- **After**: `'methodName': async function() { ... }`

### 3. Method Calls
- **Before**: `Meteor.call('method', params, callback)`
- **After**: `await Meteor.callAsync('method', params)`

### 4. User Operations
- **Before**: `Meteor.user()`, blocking user queries
- **After**: `await Meteor.userAsync()`, non-blocking async queries

### 5. HTTP Requests
- **Before**: `HTTP.call('POST', url, options)`
- **After**: `await HTTP.callAsync('POST', url, options)`

### 6. Aggregation Pipelines
- **Before**: `Meteor.wrapAsync()` wrapper around MongoDB aggregation
- **After**: Native Promise-based aggregation with proper error handling

### 7. Concurrent Operations
- **Before**: Sequential callback-based operations
- **After**: `Promise.all()` for parallel async operations where appropriate

### 8. Loop Handling
- **Before**: `forEach()` with blocking operations inside
- **After**: `for...of` loops with `await` or `Promise.all()` for concurrent processing

## Files Modified

### Server-side Database Modernization
**server/main.js**
- **Before**: `require('fs')` and synchronous file operations
- **After**: `import fs from 'fs/promises'` with async file reading
- **Before**: `Collection.rawCollection().drop().catch(() => {})`
- **After**: `Collection.rawCollection().deleteMany({})` with proper Promise handling
- **Before**: Sequential `insert()` calls in forEach loops
- **After**: `insertMany()` for bulk operations with better performance

### Profile Methods Modernization
**imports/api/profile.js**
- **Before**: `Meteor.users.find().fetch()` blocking operations
- **After**: `await Meteor.users.find().fetchAsync()` non-blocking queries
- **Before**: `Meteor.wrapAsync()` for complex operations
- **After**: Native async/await patterns with proper error handling
- **Before**: Nested callbacks for user profile checks
- **After**: Clean async/await flow with `Promise.all()` for concurrent operations

### Experiments Module Modernization
**imports/api/experiments.js**
- **Before**: `Meteor.userAsync()` mixed with synchronous operations
- **After**: Consistent async patterns throughout all methods
- **Before**: Sequential database queries in loops
- **After**: Parallel processing with `Promise.all()` for better performance
- **Before**: Complex callback chains for aggregation
- **After**: Promise-based MongoDB aggregation with proper error handling
- **Before**: Manual email sending loops
- **After**: Concurrent email sending with batched operations

### Router Modernization
**imports/api/routes.js**
- **Before**: Iron Router with `this.render()` and callback patterns
- **After**: FlowRouter with `BlazeLayout.render()` and modern syntax
- **Before**: `Router.onBeforeAction()` for authentication
- **After**: `triggersEnter` with route groups for better organization
- **Before**: Synchronous user checks in routes
- **After**: `Tracker.autorun()` for reactive user state handling
- **Before**: Mixed route definition patterns
- **After**: Consistent route groups (public vs authenticated) with proper data passing

### Template Event Handlers
**client/templates/mainfile.js**
- **Before**: `FlowRouter.go('route')` with basic patterns
- **After**: Modern FlowRouter with route parameters and reactive helpers
- **Before**: Simple template events without state management
- **After**: ReactiveVar for local state and proper lifecycle hooks
- **Before**: Direct route navigation without error handling
- **After**: Loading states and error handling in navigation
