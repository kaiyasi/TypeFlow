FROM node:20-alpine as build-stage

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies for build
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Grant read permissions to all users
RUN chmod -R 755 /usr/share/nginx/html

# Copy nginx-simple.configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:80/ || exit 1

# Expose port 80 (internal container port)
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
