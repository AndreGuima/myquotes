# Stage 1: Compile and Build angular codebase
# Use official node image as the base image
FROM node:latest as build
# Set the working directory
WORKDIR /app
# Add the source code to app
COPY . .
# Install all the dependencies
RUN npm install
# Generate the build of the application
RUN npm run build

# Stage 2: Serve app with nginx server
# Use official nginx image as the base image
FROM nginx:latest
# Copy the custom nginx configuration file to the container in the default location
COPY nginx.conf /etc/nginx/nginx.conf
# Copy the build output to replace the default nginx contents.
COPY --from=build /app/dist/myquotes/browser /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# docker build -t andrepaivaguimaraes/myquotes:latest .
# docker image ls
# docker run -d -p 8080:80 andrepaivaguimaraes/myquotes:latest
# docker ps
# inside the container ls -l /usr/share/nginx/html
