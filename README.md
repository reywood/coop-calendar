```sh
$ conda create -n coop python=3.10
```

```sh
$ conda activate coop
$ pip install -r requirements.txt
```

## Authorize credentials for a desktop application

_Copied from [these directions](https://developers.google.com/calendar/api/quickstart/python#authorize_credentials_for_a_desktop_application)._

To authenticate as an end user and access user data in your app, you need to create one or more OAuth 2.0 Client IDs. A client ID is used to identify a single app to Google's OAuth servers. If your app runs on multiple platforms, you must create a separate client ID for each platform.

1. In the [Google Cloud console](https://console.cloud.google.com/), go to [Menu menu > APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials).
2. Click Create Credentials > OAuth client ID.
3. Click Application type > Desktop app.
4. In the Name field, type a name for the credential. This name is only shown in the Google Cloud console.
5. Click Create. The OAuth client created screen appears, showing your new Client ID and Client secret.
6. Click OK. The newly created credential appears under OAuth 2.0 Client IDs.
7. Save the downloaded JSON file as credentials.json, and move the file to your working directory.
