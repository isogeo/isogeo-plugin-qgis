## Why

This module has been developed according to [Issue](https://github.com/isogeo/isogeo-plugin-qgis/issues/194).
It uses the `PyQt` library to authenticate itself to the Isogeo API (like [api_with_qt module](https://github.com/isogeo/isogeo-plugin-qgis/issues/185)).

## How to use it

1. Put the `client_secrets.json` authentication file in the `test/dev` folder.

2. Create and activate a virtual environment in the same folder :

    ``` powershell
        cd .\test\dev\search_by_keyword\
        python -m venv .venv_kwwithqt --system-site-packages
        .\.venv_kwwithqt\Scripts\activate
    ```

3. Install the [`isogeo-pysdk`](https://github.com/isogeo/isogeo-api-py-minsdk) package in your virtual environment :

    ``` powershell
        pip install isogeo-pysdk
    ```

4. Run the `kw_with_qt.py` python file in your vitual environment :

    ``` powershell
        search_by_keyword.py
    ```
