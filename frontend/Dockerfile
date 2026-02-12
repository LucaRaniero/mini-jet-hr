# Mini Jet HR - Frontend Development Container
#
# Usage (via docker-compose):
#   docker-compose up --build    Start all services
#   Vite dev server: http://localhost:5173

FROM node:20-alpine

WORKDIR /app

# Install dependencies first (Docker cache: only re-runs if package*.json changes)
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

EXPOSE 5173

# --host 0.0.0.0: expose to all network interfaces (required for Docker)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
