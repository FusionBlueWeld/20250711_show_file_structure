import os
import datetime

# 抽出対象とするファイルの拡張子と、Markdownで使う言語名を対応させます
TARGET_EXTENSIONS = {
    '.py': 'python',
    '.html': 'html',
    '.css': 'css',
    '.js': 'javascript'
}

def create_full_documentation(target_path):
    """
    指定フォルダのファイル構造と対象ソースコードを抽出し、
    1つのMarkdownファイルとしてスクリプトと同じ場所に保存します。
    """
    if not os.path.isdir(target_path):
        print(f"❌ エラー: フォルダ '{target_path}' が見つかりません。")
        return

    # ソースコードを読み込むファイルのパスを格納するリスト
    code_files = []

    # --- 1. ツリー構造を生成 & 対象ファイルをリストアップ ---
    def build_tree_and_find_code(dir_path, prefix=""):
        lines = []
        try:
            entries = sorted([e for e in os.listdir(dir_path) if e not in ['.git', '__pycache__', '.vscode', '.DS_Store']])
        except PermissionError:
            return [f"{prefix}└── [アクセス権がありません]"], []

        local_code_files = []
        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            path = os.path.join(dir_path, entry)
            
            # 対象の拡張子を持つファイルをリストに追加
            ext = os.path.splitext(entry)[1]
            if ext in TARGET_EXTENSIONS:
                relative_path = os.path.relpath(path, target_path)
                local_code_files.append(relative_path)

            if os.path.isdir(path):
                lines.append(f"{prefix}{connector}{entry}/")
                extension = "    " if is_last else "│   "
                sub_lines, sub_code_files = build_tree_and_find_code(path, prefix + extension)
                lines.extend(sub_lines)
                local_code_files.extend(sub_code_files)
            else:
                lines.append(f"{prefix}{connector}{entry}")
        
        return lines, local_code_files

    # --- 2. Markdownコンテンツの作成 ---
    base_folder_name = os.path.basename(os.path.abspath(target_path))
    
    # 2a. 説明文
    date_str = datetime.datetime.now().strftime('%Y年%m月%d日')
    description = (
        f"# 📁 {base_folder_name} のファイル構造とソースコード\n\n"
        f"**作成日:** {date_str}\n\n"
        f"**対象フォルダ:** `{target_path}`\n\n"
    )

    # 2b. ファイル構造ツリー
    tree_lines, code_files_relative = build_tree_and_find_code(target_path)
    tree_markdown = (
        "## ファイル構造\n"
        "```\n"
        f"{base_folder_name}/\n" +
        "\n".join(tree_lines) +
        "\n```\n"
    )

    # 2c. 各ファイルのソースコード
    source_code_docs = ["\n---\n\n## 各ファイルのソースコード\n"]
    for relative_path in sorted(code_files_relative):
        full_path = os.path.join(target_path, relative_path)
        ext = os.path.splitext(relative_path)[1]
        lang = TARGET_EXTENSIONS.get(ext, "")
        
        # ファイルパスの区切り文字を / に統一
        header_path = relative_path.replace(os.sep, '/')
        source_code_docs.append(f"### 📄 {header_path}\n")
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            source_code_docs.append(f"```{lang}\n{content}\n```\n")
        except Exception as e:
            source_code_docs.append(f"```\n[エラー: ファイルを読み込めませんでした - {e}]\n```\n")

    # --- 3. 最終的なコンテンツを結合 ---
    final_content = description + tree_markdown + "".join(source_code_docs)

    # --- 4. ファイルへの保存 ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = f"doc_{base_folder_name}.md"
    output_filepath = os.path.join(script_dir, output_filename)

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"✅ ドキュメントを '{output_filepath}' に保存しました。")
    except Exception as e:
        print(f"❌ ファイルの保存中にエラーが発生しました: {e}")

if __name__ == '__main__':
    # ドキュメントを生成したいフォルダのパスを指定してください
    target_folder_path = r'C:\Users\tsuts\Desktop\PythonDev_SDenv\20250720_text2img_processor4XL_KamiGazou'

    create_full_documentation(target_folder_path)