# Setup Gemini API Key

To enable AI message enhancement with Gemini, you need to set up your Gemini API key:

## Step 1: Get Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

## Step 2: Set Environment Variable

### Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

### Windows (Command Prompt):
```cmd
set GEMINI_API_KEY=your-api-key-here
```

### Windows (Permanent):
1. Press Win + R, type `sysdm.cpl`
2. Go to Advanced → Environment Variables
3. Add new System Variable:
   - Name: `GEMINI_API_KEY`
   - Value: `your-api-key-here`

## Step 3: Restart Terminal
After setting the environment variable, restart your terminal/command prompt.

## Step 4: Test
Run the complete system and try option 8 to test AI message enhancement!

## Features
- Enhances messages to be more natural and well-written
- Fixes grammar and spelling
- Maintains original tone and intent
- Works with WhatsApp messaging
- Can be extended to Gmail and other apps

## Example
- Original: "hey r u free tmrw?"
- Enhanced: "Hey! Are you free tomorrow?"