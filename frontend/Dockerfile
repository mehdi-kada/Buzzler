# Dev stage
FROM node:20-alpine
# Set the working directory
WORKDIR /app
# Install pnpm
RUN npm install -g pnpm
# Copy package files and install dependencies
COPY package*.json ./
RUN pnpm install
# Copy the rest of your source code
COPY . .
# Expose the port Next.js runs on
EXPOSE 3000
# The command to start the Next.js development server
CMD ["pnpm", "run", "dev"]
