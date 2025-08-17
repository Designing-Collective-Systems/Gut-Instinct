FROM node:20

# Install Python and required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Meteor
RUN curl https://install.meteor.com/ | sh
ENV PATH=$PATH:/root/.meteor

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY .meteor ./.meteor/

# Install Python dependencies
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy all source code
COPY . .

# Install Meteor dependencies and build
RUN meteor npm install
RUN meteor build --directory /tmp/build --server-only

# Move to the built app directory
WORKDIR /tmp/build/bundle

# Install production dependencies
RUN cd programs/server && npm install

# Copy Python scripts and other assets to the correct location
COPY public ./public/
COPY server ./server/

# Make sure Python scripts are executable
RUN find . -name "*.py" -exec chmod +x {} \;

EXPOSE 3000

CMD ["node", "main.js"]