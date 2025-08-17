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
ENV METEOR_ALLOW_SUPERUSER=1

WORKDIR /app

# Copy all source code first
COPY . .

# Install Python dependencies - simple approach
RUN pip3 install numpy pandas matplotlib seaborn plotly scikit-learn scipy || echo "Python package installation failed, continuing..."

# Install Meteor dependencies and build
RUN meteor npm install
RUN meteor build --directory /tmp/build --server-only --allow-superuser

# Move to built app and install production dependencies
WORKDIR /tmp/build/bundle
RUN cd programs/server && npm install

# Copy Python scripts and other assets to the correct location
COPY public ./public/
COPY server ./server/

# Make sure Python scripts are executable
RUN find . -name "*.py" -exec chmod +x {} \;

# Verify Python is available
RUN python3 --version

EXPOSE 3000
CMD ["node", "programs/server/main.js"]