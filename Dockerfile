FROM node:20

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Install Meteor
RUN curl https://install.meteor.com/ | sh
ENV PATH=$PATH:/root/.meteor

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY .meteor ./.meteor/

# Copy source code
COPY . .

# Install Meteor dependencies and build
RUN meteor npm install
RUN meteor build --directory /tmp/build --server-only

# Move to built app and install production dependencies
WORKDIR /tmp/build/bundle
RUN cd programs/server && npm install

# Copy your assets to the right location
WORKDIR /app
RUN cp -r public /tmp/build/bundle/ 2>/dev/null || echo "No public folder"
RUN cp -r server /tmp/build/bundle/ 2>/dev/null || echo "No server folder"

# Switch back to bundle directory
WORKDIR /tmp/build/bundle

EXPOSE 3000
CMD ["node", "main.js"]