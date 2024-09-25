# Brushee GUI

![Windows](https://img.shields.io/badge/platform-Windows-green.svg)
![Linux](https://img.shields.io/badge/platform-Linux-green.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)

## 概要

- GUI上で経由地点の編集を行うためのアプリケーション

- 現在は以下の操作が可能
    - 既存ファイルの読み込み
    - 経由地点（Node）の追加・移動・削除
    - Directionモードの変更（head or keep）
    - 編集結果の書き出し

## セットアップ

### 必要条件

- Python 3.8 or higher
- PyQt5
- PyYAML
- PIL (Pillow)

    ```bash
    pip3 install PyQt5 PyYAML Pillow
    ```

### 実行

```bash
git clone https://github.com/yourusername/brushee_gui.git
cd brushee_gui/scripts
python3 main.py
```

## 使用方法

![image](https://github.com/user-attachments/assets/40f9820f-3f44-4a4e-b2f7-39179cf69a12)

### Menu Bar
- **File**: 経由地点ファイルの読み込み，保存
    - **Open Exiting Map Elements File**: 既存の経由地点ファイルの読み込み（地図は紐づけられているものを開く）
    - **Create New Map Elements File**: 地図を選択し，新規ファイル作成
    - **Overwrite Map Elements File**: 上書き保存
    - **Save As Map Elements File**: 名前を付けて保存

    保存の際，地図は自動的に紐づけられる
- **Edit**: 未実装
- **View**: 未実装
- **Help**: 未実装

### Editor Toolbar
- **Select**: 要素情報確認，NodeのDirection変更（head or keep）
- **Add node**: 経由地点追加
- **Move element**: 要素移動
- **Delete element**: 要素削除
- **Paint map**: 未実装
- **Erase map**: 未実装
