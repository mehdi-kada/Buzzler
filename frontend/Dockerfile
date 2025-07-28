# Dev stage
FROM node:20-alpine
# Set the working directory
WORKDIR /app
# Copy package files and install dependencies
# Using 'npm install' instead of 'ci' is fine for development
COPY package*.json ./
RUN npm install
# Copy the rest of your source code
COPY . .
# Expose the port Next.js runs on
EXPOSE 3000
# The command to start the Next.js development server
CMD ["npm", "run", "dev"]
