// Create this file in the client directory to run once when the application starts
import { Meteor } from 'meteor/meteor';

// This code will run once when the client application starts
Meteor.startup(() => {
  // Function to handle duplicate renders
  const handleDuplicateRenders = () => {
    // Select all elements with ID ga-main
    const mainElements = document.querySelectorAll('#ga-main');
    
    // If more than one element found, remove the duplicates
    if (mainElements.length > 1) {
      // Keep the first one, remove the rest
      for (let i = 1; i < mainElements.length; i++) {
        mainElements[i].parentNode.removeChild(mainElements[i]);
      }
    }
  };
  
  // Run immediately and then periodically check for duplicates
  handleDuplicateRenders();
  setInterval(handleDuplicateRenders, 500);
});