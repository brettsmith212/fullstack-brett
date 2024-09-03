---
title:  "Digital Ocean VPS - Docker + Next.js Deployment"
date:   2024-08-25
---

The fastest way to deploy code to production for solo hackers (and only $4/month):
<br>
*Write code > push to Github > create docker image > push image to Digital Ocean VPS > start container*

## Digital Ocean Droplet Setup

### 1. digitalocean.com
Create Droplet

Authentication Method - SSH Key

**local machine:**

`ssh-keygen -f digitalocean`

`cat .ssh/id_rsa_digitalocean.pub`

Copy & Paste this key into SSH Key box on digital ocean

### 2. SSH into remote machine
`ssh root@ip_address`

`apt-get update`

`apt-get upgrade`

check that *local machine:*`.ssh/id_rsa_digitalocean.pub` value is found in *remote machine:*`.ssh/authorized_keys`

### 3. Setup SSH keys in remote machine
**remote machine:**

`mkdir .ssh`

`touch .ssh/authorized_keys`

copy *local machine* `.ssh/id_rsa.pub` to *remote machine* `.ssh/authorized_keys`

## Using Docker w/ Next.js in Droplet Setup

### 1. Add snippet to `next.config.js`
```typescript
const nextConfig = {
	output: "standalone"
}
```

### 2. Create `Dockerfile` and `.dockerignore`
- <a href="https://github.com/vercel/next.js/blob/canary/examples/with-docker/Dockerfile" target="_blank">Dockerfile Example</a>
- <a href="https://github.com/vercel/next.js/blob/canary/examples/with-docker/.dockerignore" target="_blank">.dockerignore Example</a>

- Use [8. Setup Dockerfile](#8-setup-dockerfile-supabase-edition) for Dockerfile w/ Supabase Env Variables
- Run locally with `docker run -p 3000:3000 <repo-name>`

### 3. Github Package Registry
1. `github.com/<github-username>` > Settings > Developer Settings > Personal Access Tokens > Tokens (classic)
2. Generate New Token > Generate New Token (classic)
	- Note = `project-name`
	- Expiration
	- `write:packages`, `read:packages`, `delete:packages` selected
3. Generate Token
	- Copy the personal access token (PAT) generated and save for later use

### 4. Build Docker Image & Upload to Github Package Registry
1. Build Image: `docker build . --platform linux/amd64 -t ghcr.io/<github-username>/<repo-name>`
2. Login to Docker Registry: `docker login ghcr.io`
	- Username: `<github-username>`
	- Password: Personal Access Token (PAT) generated in step 3.3
	- `Login Succeeded` message should appear
3. `docker push ghcr.io/<github-username>/<repo-name>`
4. Docker image should be showing in `Packages` Github tab

### 5. Running Docker Image on Digital Ocean Droplet
1. Check that Docker is installed with `systemctl is-active docker`
2. If it returns `inactive`,
	- Install Docker using `apt-get install docker.io` or <a href="https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04" target="_blank">Digital Ocean Docker Instructions</a>
	- `systemctl is-active docker` should say `active` now
3. Test docker w/ `docker run hello-world`
4. Login to Docker Registry: `docker login ghcr.io`
	- Username: `<github-username>`
	- Password: Personal Access Token (PAT) generated in step 3.3
	- `Login Succeeded` message should appear
5. Start container with `docker run -d -p 3000:3000 --name <container-name> --restart always ghcr.io/<github-username>/<repo-name>`

### 6. Setup SSL
1. <a href="https://certbot.eff.org/" target="_blank">Certbot</a> -> Follow steps
 - Nginx -> Ubuntu

### 7. Enable Firewall on Digital Ocean Droplet (using `ufw` firewall in Ubuntu)
1. See apps using `ufw app list`
2. Allow OpenSSH `ufw allow OpenSSH`
	- If using nginx `ufw allow "Nginx Full"`
3. Enable `ufw enable`
4. See new rules `ufw status`
	- This shows the only ports available

### 8. Setup Dockerfile (Supabase Edition)

```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
	if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
	elif [ -f package-lock.json ]; then npm ci; \
	elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
	else echo "Lockfile not found." && exit 1; \
	fi


# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_SUPABASE_URL
ARG SUPABASE_SERVICE_ROLE_KEY
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
# ENV NEXT_TELEMETRY_DISABLED 1

RUN \
	if [ -f yarn.lock ]; then yarn run build; \
	elif [ -f package-lock.json ]; then npm run build; \
	elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm run build; \
	else echo "Lockfile not found." && exit 1; \
	fi

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_SUPABASE_URL
ARG SUPABASE_SERVICE_ROLE_KEY
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY

# Uncomment the following line in case you want to disable telemetry during runtime.
# ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/next-config-js/output
CMD HOSTNAME="0.0.0.0" node server.js
```

### 9. Setup Github Actions

1. `<respository-name>` > Settings > Secrets and variables > Actions
2. Setup Repository Secrets
- `DO_HOST`: Droplet IP Address
- `DO_USERNAME`: root
- `GHCR_PAT`: PAT generated in step 3.3
- `SSH_PRIVATE_KEY`: Private Key from step 1 (cat .ssh/id_rsa_digitalocean)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: from supabase
- `NEXT_PUBLIC_SUPABASE_URL`: from supabase
- `SUPABASE_SERVICE_ROLE_KEY`: from supabase

3. Create File: `.github/workflows/docker-build-push.yaml`

```yaml
name: Docker Build, Push, and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-push-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GHCR_PAT }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          platforms: linux/amd64
          build-args: |
            NEXT_PUBLIC_SUPABASE_ANON_KEY=${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
            NEXT_PUBLIC_SUPABASE_URL=${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
            SUPABASE_SERVICE_ROLE_KEY=${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}

      - name: Deploy to DigitalOcean
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          DO_HOST: ${{ secrets.DO_HOST }}
          DO_USERNAME: ${{ secrets.DO_USERNAME }}
        run: |
          echo "$SSH_PRIVATE_KEY" > private_key && chmod 600 private_key
          ssh -o StrictHostKeyChecking=no -i private_key ${DO_USERNAME}@${DO_HOST} '
            docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            docker stop shipfast-test || true
            docker rm shipfast-test || true
            docker run -d -p 3000:3000 --name shipfast-test --restart always ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          '
```

### Resources

<a href="https://www.youtube.com/watch?v=DfNhBZUrA-U&t=78s" target="_blank">Deploy Docker Image to VPS</a>

<a href="https://www.youtube.com/watch?v=vj34hX8jWM0&t=1s" target="_blank">Setup Digital Ocean Droplet w/ Next.js</a>
