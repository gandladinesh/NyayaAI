# =====================================================================
# NyayaAI Frontend Multi-Stage Dockerfile
# =====================================================================

# Stage 1: Build static assets with Node.js
FROM node:20-alpine AS build

WORKDIR /app

# Copy package descriptors
COPY package*.json ./
RUN npm ci

# Copy frontend source
COPY . .

# Build for production
RUN npm run build

# Stage 2: Serve with lightweight NGINX
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
