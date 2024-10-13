# add-dictionary
OpenJTalkのユーザ辞書をGUIで追加するアプリ


# 使い方

YouTube デモ動画\
https://youtu.be/v1CMfifnyPA?si=1znBLJhBMRGVfWjb

## 仮想環境の作成

```
py -m venv .venv
.venv\Scripts\activate
```

必要なライブラリのインストール
```
pip freeze > requirements.txt
```

## できること

- 辞書に単語を追加
- 単語の編集
- 単語の削除

### 初めにすること

初期のユーザ辞書にuser_dict.csvを準備しています。

別ファイルにユーザ辞書に単語を追加したい場合、左上の設定から「保存/読み込み」を選択します。\
csvファイルの辞書を選択します。\
※csvファイルしか選択できないようになっています。


「追加、編集、削除」のラジオボタンがあります。どの操作を行うか選択します。

### 追加操作

1. 単語入力に追加したい単語を入力します。
    - 自動的に単語のカタカナが「読み編集、読み（カタカナ）、発音編集、発音（カタカナ）」に入力されます。

1. 単語の読みが違えば「読み編集」から編集します。
    - 「読み編集」を編集すると「発音編集、発音（カタカナ）」も同時に変換されます。

1. 単語の発音を変えるには「発音編集」から編集します。
    - 「発音（カタカナ）」だけが変換されます。

1. 「コスト、品詞、品詞細分類、活用語、アクセント結合規制」はすでに入力されているものを使います。

1. 単語のアクセントをつけます。
    - 例えば、「VITS二（ビッツツー）」の最後のツにアクセントをつけたいとき、音素数が「5」になります。最後のツは5音素中4番目になるので4を設定。

1. 追加ボタンを押せば辞書に追加されます。

### 編集操作

1. 編集のラジオボタンを選択します。
1. 右のテーブルから単語を選択します。すると、自動的に入力に情報が記入されます。
1. 編集したいものを書き換えます。
1. 更新ボタンを押すと辞書が更新されます。

>「編集中でもカナ変換の有効化」について
>
>編集の選択をしているときは単語を書き換えても「読み編集、読み（カタカナ）、発音編集、発音（カタカナ）」に変化が起こらないようになっています。
>
>「編集中でもカナ変換の有効化」にチェックを入れれば、追加の様に単語を編集したときに「読み編集、読み（カタカナ）、発音編集、発音（カタカナ）」に自動的にカタカナが入力されます。

### 削除操作

1. テーブルから単語を選択します。
1. 削除ボタンを押します。
1. 辞書から単語か消え、テーブルが更新されます。