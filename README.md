# ハッカソン用データセット作成コード
使用ライブラリ
```python:
selenium
pandas
```

## ファイル解説
main_page.py

PC上でtiktokを開くと一番最初に出てくるページからデータ収集。
無限スクロールして指定した数のデータを取得。
トップページでは15秒以上の動画が多く、機械学習には不向き。

search.py

検索ワードをいれ、指定の個数データをとってくるプログラム。
こちらは15秒程の動画が多いが、検索ワードとは別の動画がたまに入る。
また、シェア数は取得できなかった。