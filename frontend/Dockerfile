FROM node:20

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Configure npm and install dependencies
RUN npm config set strict-ssl false \
    && npm config set registry https://registry.npmmirror.com/ \
    && npm set fetch-timeout 120000 \
    && npm set fetch-retries 20 \
    && npm install -g npm@latest \
    && npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

EXPOSE 3000

CMD ["npm", "start"]