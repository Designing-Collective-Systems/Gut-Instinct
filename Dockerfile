FROM node:20

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Install Meteor
RUN curl https://install.meteor.com/ | sh
ENV PATH=$PATH:/root/.meteor

WORKDIR /app
COPY . .

# Install Python dependencies only if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; else echo "No requirements.txt found, skipping Python packages"; fi

# Install Meteor dependencies and build
RUN meteor npm install
RUN meteor build --directory /tmp/build --server-only

# Move to built app and install production dependencies
WORKDIR /tmp/build/bundle
RUN cd programs/server && npm install

# Copy Python scripts and other assets
COPY public /tmp/build/bundle/public/
COPY server /tmp/build/bundle/server/

# Make sure Python scripts are executable
RUN find . -name "*.py" -exec chmod +x {} \;

EXPOSE 3000
CMD ["node", "main.js"]