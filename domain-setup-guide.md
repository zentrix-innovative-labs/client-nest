# Domain Setup Guide for ClientNest

## Overview
This guide will help you connect your frontend on Vercel to your backend on AWS using your custom domain `clientnest.xyz`.

## Step 1: Deploy Backend to AWS

1. **Deploy the updated CloudFormation stack:**
   ```bash
   aws cloudformation deploy \
     --template-file clientnest-vpc.yaml \
     --stack-name nest \
     --capabilities CAPABILITY_NAMED_IAM \
     --parameter-overrides DatabasePassword=YourSecurePassword123 \
     --region af-south-1
   ```

2. **Get the Load Balancer DNS name:**
   ```bash
   aws cloudformation describe-stacks --stack-name nest --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' --output text --region af-south-1
   ```

## Step 2: Configure Namecheap DNS

1. **Log into Namecheap** and go to your domain `clientnest.xyz`

2. **Add DNS Records:**
   - **A Record for Frontend:**
     - Host: `@` (or leave blank)
     - Value: Your Vercel IP (get from Vercel dashboard)
     - TTL: Automatic
   
   - **CNAME for API:**
     - Host: `api`
     - Value: Your AWS Load Balancer DNS name
     - TTL: Automatic
   
   - **CNAME for www:**
     - Host: `www`
     - Value: Your Vercel domain or `clientnest.xyz`
     - TTL: Automatic

## Step 3: Configure Vercel Frontend

1. **In your Vercel project settings:**
   - Add custom domain: `clientnest.xyz`
   - Add custom domain: `www.clientnest.xyz`

2. **Update your frontend environment variables:**
   ```env
   REACT_APP_API_URL=https://api.clientnest.xyz
   # or
   VITE_API_URL=https://api.clientnest.xyz
   ```

3. **Update your frontend API calls to use the new domain:**
   ```javascript
   // Instead of localhost:8000
   const API_BASE_URL = 'https://api.clientnest.xyz';
   ```

## Step 4: SSL Certificate (Optional but Recommended)

1. **For AWS Load Balancer:**
   - Request SSL certificate in AWS Certificate Manager
   - Add HTTPS listener to load balancer
   - Update CloudFormation template to include SSL

2. **For Vercel:**
   - Vercel automatically provides SSL certificates
   - No additional configuration needed

## Step 5: Test the Connection

1. **Test Backend Health:**
   ```bash
   curl https://api.clientnest.xyz/api/health/
   ```

2. **Test Frontend:**
   - Visit `https://clientnest.xyz`
   - Should load your Vercel frontend

3. **Test API Integration:**
   - Frontend should be able to call `https://api.clientnest.xyz/api/...`

## DNS Propagation

- DNS changes can take up to 48 hours to propagate globally
- Usually works within 15-30 minutes
- You can check propagation using: https://www.whatsmydns.net/

## Troubleshooting

1. **If backend is not accessible:**
   - Check AWS security groups
   - Verify load balancer health checks
   - Check EC2 instance logs

2. **If frontend can't connect to backend:**
   - Verify CORS settings in Django
   - Check API URL in frontend
   - Test API endpoints directly

3. **If domain doesn't resolve:**
   - Check DNS records in Namecheap
   - Wait for DNS propagation
   - Verify domain configuration in Vercel

## Security Considerations

1. **Environment Variables:**
   - Store sensitive data in AWS Secrets Manager
   - Use environment variables in Vercel
   - Never commit secrets to Git

2. **CORS Configuration:**
   - Only allow your specific domains
   - Configure proper credentials handling

3. **SSL/TLS:**
   - Always use HTTPS in production
   - Configure proper SSL certificates

## Next Steps

1. Set up monitoring and logging
2. Configure backup strategies
3. Set up CI/CD pipelines
4. Implement proper error handling
5. Add rate limiting and security headers 