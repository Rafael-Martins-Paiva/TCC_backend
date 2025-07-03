#!/bin/bash

# Base URL for the API
BASE_URL="http://localhost:8000/api/v1/accounts"

echo "--- Testing User Registration ---"
# Replace with a unique email for each test run
http --json --ignore-stdin POST $BASE_URL/register/ email="test_$(date +%s)@example.com" name="Test User" password="your_strong_password" password2="your_strong_password"

echo -e "\n--- Testing Resend Verification Email (requires a registered email) ---"
# Replace with an email that has been registered
http --json --ignore-stdin POST $BASE_URL/resend-verification-email/ email="test@example.com"

echo -e "\n--- Testing Email Verification (requires email and token from registration email) ---"
# IMPORTANT: You need to get the verification token from the email sent to the registered user.
# This token is usually found in the verification link.
# Replace 'your_registered_email@example.com' and 'YOUR_VERIFICATION_TOKEN' with actual values.
http --json --ignore-stdin POST $BASE_URL/verify-email/ email="your_registered_email@example.com" token="YOUR_VERIFICATION_TOKEN"

echo -e "\n--- Testing Change Password (requires authentication token) ---"
# IMPORTANT: You need to obtain an authentication token first (e.g., by logging in).
# This script does not include a login endpoint.
# Replace 'YOUR_AUTH_TOKEN' with a valid JWT or session token.
# Replace 'your_old_password' and 'your_new_password' with actual values.
# This endpoint requires the user to be authenticated.
# Example: http POST http://localhost:8000/api/token/ "username=your_registered_email@example.com" "password=your_old_password"
# Then use the 'access' token from the response.
AUTH_TOKEN="YOUR_AUTH_TOKEN"
http --json --ignore-stdin POST $BASE_URL/change-password/ "Authorization: Bearer $AUTH_TOKEN" old_password="your_old_password" new_password="your_new_password" confirm_new_password="your_new_password"
