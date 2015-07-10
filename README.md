# 1984 Random Quoter

2015.07.1x  Python Web Meetup

## 環境設定

Python 3.4，又以 Python 3.4.4+ 為優。

- Tornado (Apache 2.0 License)
- aiohttp (Apache 2.0 License)
- asyncio (Python 3.3 use `pip install asyncio`)
- colorlog (MIT License)
- IPython Notebook (BSD License)


## 使用

1. Python 環境設定，建議使用虛擬環境。
    
    ```bash
    pip install -r requirements.txt
    ```
    
2. 執行 `0_parse_1984.py`：自[古騰堡電子書計畫][gutenberg proj]下載 1984 文本。

    ```bash
    python 0_parse_1984.py
    ```
   
   成功下載後同目錄下會多一個 `parsed_1984.pkl` pickle 完的文本檔案。
    
3. 執行 `random_quote_app.py`：開啟引言產生器 REST server（使用 Tornado）。

    ```bash
    python random_quote_app.py --num_process=1
    ```
    
   預設跑在 <http://localhost:9527>。
   之後會一直打這個 API，如果要減少輸出訊息，可以提高 logging 觸發門檻：
   
    ```bash
    python random_quote_app.py --num_process=1 --logging=warning
    ```

   更多的選項可以參考 `--help` 說明
   
4. 跟著跑 `1_demo.ipynb` 執行不同方法的嘗試。首先需要打開 IPython Notebook Server，

    ```bash
    ipython notebook
    ```
    
   預設會打開瀏覽器進入 IPython notebook <http://localhost:8888>。
   
5. 或者直接執行 `2_console_demo.py` 看最後的結果。

    ```bash
    python 2_console_demo.py
    ```

[gutenberg proj]: https://www.gutenberg.org/


## License

The slide is powered by

- [shower.js]: HTML5 slideshow framework by Vadim Makeev *et al.*, under MIT license
- [highlight.js]: Syntax highlight library by Ivan Sagalaev *et al.*, under MIT license

Unless explicitly stated,

- the content of the slides (at `slides` folder) is shared under Creative Commons 4.0 BY licesne.
- the code is shared under MIT license.

More information about license at [CC Attribution 4.0] and `LICENSE_MIT`.

[reveal.js]: https://github.com/hakimel/reveal.js
[shower.js]: https://github.com/shower/shower
[highlight.js]: http://highlightjs.org/
[CC Attribution 4.0]: https://creativecommons.org/licenses/by/4.0/
