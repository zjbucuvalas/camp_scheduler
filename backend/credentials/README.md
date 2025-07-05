# Calendar Agent Credentials

This directory stores Google Calendar API credentials for the Calendar Agent.

## Required Files

1. **credentials.json** - OAuth client credentials from Google Cloud Console
2. **token.pickle** - Authentication token (auto-generated after first login)

## Setup Instructions

1. Follow the setup guide in `../CALENDAR_SETUP.md`
2. Download your OAuth credentials from Google Cloud Console
3. Rename the downloaded file to `credentials.json`
4. Place it in this directory

## Important Security Notes

- **NEVER commit credential files to version control**
- These files contain sensitive authentication information
- The `.gitignore` file is configured to exclude these files
- Only the `README.md` file in this directory should be committed

## File Structure

```
credentials/
├── README.md          # This file (committed to git)
├── credentials.json   # OAuth credentials (NOT committed)
└── token.pickle       # Auth token (NOT committed)
```

## Troubleshooting

If you encounter authentication issues:

1. Ensure `credentials.json` is in this directory
2. Delete `token.pickle` to force re-authentication
3. Check that Google Calendar API is enabled in Google Cloud Console
4. Verify OAuth consent screen is properly configured 