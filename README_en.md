[日本語](README.md) | [English](README_en.md)

# slack-guest-inspection

This is a script that looks for "multichannel guests that belong to one or fewer channels" in all workspaces in the Slack EnterpriseGrid environment, lists them, and outputs them to csv.

## How to use

### prepare

* Prepare a token for the SlackApp. The required permissions are as follows
  * `discovery:read`
* Clone this project and create a `config.ini` file.

### run

* Run `main.py`.
* Runs while outputting the execution status to stdout.
* Since the Slack WebAPI is executed in a loop, it may take some time if the number of users to be surveyed is large. If there is a possibility that the SlackAPI RateLimit has been reached, it will sleep for up to 61 seconds and continue to run, but if it still fails, it will throw an exception and the script will terminate.
* Output the results to `OUTPUT.csv` when the scrutiny is complete.
  * If the `OUTPUT.csv` file already exists, it will be overwritten. If you don't want to lose the past execution results, save the file beforehand.

## information

* This script is designed to work without the need for external python libraries, and does not use the SlackSDK.
* I'm not sure if `inspection` is the right word for this application. If you have a better word, please let me know. 🙇
