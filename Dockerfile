# Use the latest version of Node as the base image
FROM node:latest

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in package.json
RUN npm install

# Make port 4200 available to the world outside this container
EXPOSE 4200

# Run the app when the container launches
CMD ["npm", "start"]
