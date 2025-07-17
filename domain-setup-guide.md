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
   aws cloudformation describe-stacks --stack-name nest --region af-south-1 --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" --output text
   ```

## Step 2: Configure Namecheap DNS

1. **Log into Namecheap** and go to your domain `