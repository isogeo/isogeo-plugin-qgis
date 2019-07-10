## Why

This module has been developed according to [Issue](https://github.com/isogeo/isogeo-plugin-qgis/issues/185).
It uses the `PyQt` library to authenticate itself to the Isogeo API using an application's authentication file. Once the token is obtained, it is used to make a simple query about the resources available with the application. The [`isogeo-pysdk`](https://github.com/isogeo/isogeo-api-py-minsdk) package is used to validate the quality of the result obtained with PyQt and exclude potential causes of malfunction.

## How to use it

1. Put the `client_secrets.json` authentication file in the `test/dev/api_auth_with_qt/external_module` folder.

2. Create and activate a virtual environment in the same folder :

    ```powershell
    cd .\test\dev\api_auth_with_qt\external_module\
    python -m venv .venv_authwithqt --system-site-packages
    .\.venv_authwithqt\Scripts\activate
    ```

3. Install the [`isogeo-pysdk`](https://github.com/isogeo/isogeo-api-py-minsdk) package in your virtual environment :

    ```powershell
    python -m pip install isogeo-pysdk==2.21.*
    ```

4. Run the `api_with_qt.py` python file in your vitual environment :

    ```powershell
    python api_with_qt.py
    ```
