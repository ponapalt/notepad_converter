import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Menu, Frame, Button
import json
import yaml

class JSONYAMLNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("メモ帳 - JSON/YAML コンバーター")
        self.root.geometry("800x600")
        
        # 現在のファイルパス
        self.current_file = None
        
        # Undo/Redo用の履歴スタック
        self.undo_stack = []
        self.redo_stack = []
        
        # ツールバーフレーム作成
        self.toolbar = Frame(self.root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # 変換ボタンを追加
        self.json_to_yaml_btn = Button(self.toolbar, text="JSON → YAML", command=self.json_to_yaml)
        self.json_to_yaml_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.yaml_to_json_btn = Button(self.toolbar, text="YAML → JSON", command=self.yaml_to_json)
        self.yaml_to_json_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # テキストエリア作成（undo機能を有効化）
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("メイリオ", 10), 
                                                  undo=True, maxundo=1000, autoseparators=True)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # テキストが変更されたときのイベントを監視
        self.text_area.bind("<<Modified>>", self.on_text_modified)
        self.text_area.bind("<Key>", self.on_key_press)
        self.last_content = ""
        
        # メニューバー作成
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Fileメニュー
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="ファイル", menu=self.file_menu)
        self.file_menu.add_command(label="新規作成", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="開く", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="名前を付けて保存", command=self.save_as, accelerator="Ctrl+Shift+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="印刷", command=self.print_file, accelerator="Ctrl+P")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="終了", command=self.exit_app)
        
        # Editメニュー
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="編集", menu=self.edit_menu)
        self.edit_menu.add_command(label="元に戻す", command=self.undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="やり直し", command=self.redo, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="切り取り", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        self.edit_menu.add_command(label="コピー", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        self.edit_menu.add_command(label="貼り付け", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        self.edit_menu.add_command(label="削除", command=self.delete_selected, accelerator="Del")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="検索", command=self.find_text, accelerator="Ctrl+F")
        self.edit_menu.add_command(label="置換", command=self.replace_text, accelerator="Ctrl+H")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="すべて選択", command=self.select_all, accelerator="Ctrl+A")
        self.edit_menu.add_command(label="日付と時刻", command=self.insert_datetime)
        
        # 表示メニュー
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="表示", menu=self.view_menu)
        self.word_wrap = tk.BooleanVar()
        self.word_wrap.set(True)
        self.view_menu.add_checkbutton(label="右端で折り返す", variable=self.word_wrap, command=self.toggle_word_wrap)
        
        # フォント設定
        self.font_menu = Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label="フォント", menu=self.font_menu)
        self.font_menu.add_command(label="フォント設定", command=self.choose_font)
        
        # 変換メニュー
        self.convert_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="変換", menu=self.convert_menu)
        self.convert_menu.add_command(label="JSONからYAMLへ変換", command=self.json_to_yaml, accelerator="F5")
        self.convert_menu.add_command(label="YAMLからJSONへ変換", command=self.yaml_to_json, accelerator="F6")
        self.convert_menu.add_separator()
        self.convert_menu.add_command(label="JSONフォーマット整形", command=self.format_json, accelerator="F7")
        self.convert_menu.add_command(label="YAMLフォーマット整形", command=self.format_yaml, accelerator="F8")
        
        # ヘルプメニュー
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="ヘルプ", menu=self.help_menu)
        self.help_menu.add_command(label="ヘルプの表示", command=self.show_help)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="このアプリについて", command=self.show_about)
        
        # キーボードショートカット
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_as())
        self.root.bind("<Control-p>", lambda event: self.print_file())
        self.root.bind("<Control-f>", lambda event: self.find_text())
        self.root.bind("<Control-h>", lambda event: self.replace_text())
        self.root.bind("<Control-a>", lambda event: self.select_all())
        self.root.bind("<Control-z>", lambda event: self.undo())
        self.root.bind("<Control-y>", lambda event: self.redo())
        self.root.bind("<F5>", lambda event: self.json_to_yaml())
        self.root.bind("<F6>", lambda event: self.yaml_to_json())
        self.root.bind("<F7>", lambda event: self.format_json())
        self.root.bind("<F8>", lambda event: self.format_yaml())
        
        # 右クリックメニュー
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="元に戻す", command=self.undo)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="切り取り", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="コピー", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="貼り付け", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.context_menu.add_command(label="削除", command=self.delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="すべて選択", command=self.select_all)
        self.text_area.bind("<Button-3>", self.show_context_menu)
        
        # ステータスバー
        self.status_bar = tk.Label(root, text="準備完了", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 文字カウント表示用のステータスバー部分
        self.char_count = tk.Label(self.status_bar, text="文字数: 0")
        self.char_count.pack(side=tk.RIGHT, padx=5)
        
        # テキスト変更時に文字数を更新
        self.text_area.bind("<<Modified>>", self.update_char_count)
    
    def on_text_modified(self, event=None):
        """テキストが変更されたときに呼ばれるメソッド"""
        if self.text_area.edit_modified():
            content = self.text_area.get("1.0", tk.END+"-1c")
            self.char_count.config(text=f"文字数: {len(content)}")
            # 文字数更新後にmodifiedフラグをリセット
            self.text_area.edit_modified(False)
    
    def on_key_press(self, event=None):
        """キー入力時に編集区切りを挿入"""
        # スペースキーか改行時に編集区切りを挿入
        if event.char == " " or event.keysym == "Return":
            self.text_area.edit_separator()
    
    def save_undo_state(self):
        """現在の状態をundo履歴に保存"""
        current_content = self.text_area.get("1.0", tk.END+"-1c")
        if current_content != self.last_content:
            self.text_area.edit_separator()
            self.last_content = current_content
            
    def update_char_count(self, event=None):
        """文字数を更新（既存メソッドを修正）"""
        self.on_text_modified()
    
    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def delete_selected(self):
        try:
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass  # 選択がない場合は何もしない
    
    def find_text(self):
        # 簡易検索ダイアログを表示
        search_window = tk.Toplevel(self.root)
        search_window.title("検索")
        search_window.geometry("300x100")
        search_window.transient(self.root)
        search_window.resizable(False, False)
        
        tk.Label(search_window, text="検索する文字列:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        search_entry = tk.Entry(search_window, width=30)
        search_entry.grid(row=0, column=1, padx=5, pady=5)
        search_entry.focus_set()
        
        def search():
            query = search_entry.get()
            if query:
                start_pos = self.text_area.search(query, "1.0", tk.END)
                if start_pos:
                    line, char = map(int, start_pos.split('.'))
                    end_pos = f"{line}.{char + len(query)}"
                    self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                    self.text_area.tag_add(tk.SEL, start_pos, end_pos)
                    self.text_area.mark_set(tk.INSERT, start_pos)
                    self.text_area.see(start_pos)
                else:
                    messagebox.showinfo("検索結果", f"「{query}」は見つかりませんでした")
        
        tk.Button(search_window, text="検索", command=search).grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)
    
    def replace_text(self):
        # 簡易置換ダイアログを表示
        replace_window = tk.Toplevel(self.root)
        replace_window.title("置換")
        replace_window.geometry("300x150")
        replace_window.transient(self.root)
        replace_window.resizable(False, False)
        
        tk.Label(replace_window, text="検索する文字列:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        search_entry = tk.Entry(replace_window, width=30)
        search_entry.grid(row=0, column=1, padx=5, pady=5)
        search_entry.focus_set()
        
        tk.Label(replace_window, text="置換後の文字列:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        replace_entry = tk.Entry(replace_window, width=30)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def replace():
            query = search_entry.get()
            replacement = replace_entry.get()
            if query:
                content = self.text_area.get("1.0", tk.END+"-1c")
                new_content = content.replace(query, replacement)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, new_content)
                self.status_bar.config(text=f"置換完了: {query} → {replacement}")
        
        tk.Button(replace_window, text="すべて置換", command=replace).grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)
    
    def insert_datetime(self):
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.text_area.insert(tk.INSERT, now)
    
    def toggle_word_wrap(self):
        if self.word_wrap.get():
            self.text_area.config(wrap=tk.WORD)
        else:
            self.text_area.config(wrap=tk.NONE)
    
    def choose_font(self):
        # 簡易フォント選択ダイアログを表示
        font_window = tk.Toplevel(self.root)
        font_window.title("フォント設定")
        font_window.geometry("300x200")
        font_window.transient(self.root)
        
        # フォントファミリー
        tk.Label(font_window, text="フォント:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        font_families = ["メイリオ", "MS ゴシック", "MS 明朝", "Arial", "Times New Roman", "Courier New"]
        font_var = tk.StringVar(value="メイリオ")
        font_menu = tk.OptionMenu(font_window, font_var, *font_families)
        font_menu.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # フォントサイズ
        tk.Label(font_window, text="サイズ:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        size_var = tk.IntVar(value=10)
        size_menu = tk.OptionMenu(font_window, size_var, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24)
        size_menu.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        def apply_font():
            self.text_area.config(font=(font_var.get(), size_var.get()))
            font_window.destroy()
        
        tk.Button(font_window, text="適用", command=apply_font).grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)
    
    def print_file(self, event=None):
        messagebox.showinfo("印刷", "印刷機能は現在準備中です")
    
    def new_file(self):
        if self.text_area.get("1.0", tk.END+"-1c"):
            if messagebox.askyesno("確認", "内容が保存されていません。新規作成してもよろしいですか？"):
                # 新規作成前に編集区切りを挿入
                self.text_area.edit_separator()
                self.text_area.delete("1.0", tk.END)
                # 削除後に編集区切りを挿入
                self.text_area.edit_separator()
                self.last_content = ""
                
                self.current_file = None
                self.root.title("メモ帳 - JSON/YAML コンバーター")
        else:
            self.text_area.delete("1.0", tk.END)
            self.current_file = None
            self.root.title("メモ帳 - JSON/YAML コンバーター")
    
    def open_file(self):
        if self.text_area.get("1.0", tk.END+"-1c") and not self.current_file:
            if not messagebox.askyesno("確認", "内容が保存されていません。開いてもよろしいですか？"):
                return
        
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("テキストファイル", "*.txt"), 
                ("JSON ファイル", "*.json"), 
                ("YAML ファイル", "*.yaml;*.yml"), 
                ("すべてのファイル", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                
                # ファイルを開く前に編集区切りを挿入
                self.text_area.edit_separator()
                
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, content)
                
                # ファイルを開いた後に編集区切りを挿入
                self.text_area.edit_separator()
                self.last_content = content
                
                self.current_file = file_path
                self.root.title(f"{file_path} - メモ帳")
                self.status_bar.config(text=f"ファイルを開きました: {file_path}")
            except Exception as e:
                messagebox.showerror("エラー", f"ファイルを開けませんでした: {str(e)}")
    
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get("1.0", tk.END+"-1c")
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(content)
                self.status_bar.config(text=f"保存しました: {self.current_file}")
                return True
            except Exception as e:
                messagebox.showerror("エラー", f"保存できませんでした: {str(e)}")
                return False
        else:
            return self.save_as()
    
    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("テキストファイル", "*.txt"), 
                ("JSON ファイル", "*.json"), 
                ("YAML ファイル", "*.yaml;*.yml"), 
                ("すべてのファイル", "*.*")
            ]
        )
        
        if file_path:
            try:
                content = self.text_area.get("1.0", tk.END+"-1c")
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f"{file_path} - メモ帳")
                self.status_bar.config(text=f"保存しました: {file_path}")
                return True
            except Exception as e:
                messagebox.showerror("エラー", f"保存できませんでした: {str(e)}")
                return False
        return False
    
    def exit_app(self):
        if self.text_area.get("1.0", tk.END+"-1c") and not self.current_file:
            if messagebox.askyesno("確認", "内容が保存されていません。終了してもよろしいですか？"):
                self.root.destroy()
        else:
            self.root.destroy()
    
    def select_all(self, event=None):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return "break"
    
    def json_to_yaml(self):
        content = self.text_area.get("1.0", tk.END+"-1c")
        if not content.strip():
            messagebox.showinfo("情報", "変換するテキストがありません")
            return
        
        try:
            # 変換前に編集区切りを挿入
            self.text_area.edit_separator()
            
            # JSONをパース
            json_data = json.loads(content)
            # YAMLに変換
            yaml_data = yaml.dump(json_data, allow_unicode=True, sort_keys=False)
            # テキストエリアを更新
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, yaml_data)
            
            # 変換後に編集区切りを挿入
            self.text_area.edit_separator()
            self.last_content = yaml_data
            
            self.status_bar.config(text="JSONからYAMLに変換しました")
        except json.JSONDecodeError as e:
            messagebox.showerror("エラー", f"JSONの解析に失敗しました: {str(e)}")
        except Exception as e:
            messagebox.showerror("エラー", f"変換中にエラーが発生しました: {str(e)}")
    
    def yaml_to_json(self):
        content = self.text_area.get("1.0", tk.END+"-1c")
        if not content.strip():
            messagebox.showinfo("情報", "変換するテキストがありません")
            return
        
        try:
            # 変換前に編集区切りを挿入
            self.text_area.edit_separator()
            
            # YAMLをパース
            yaml_data = yaml.safe_load(content)
            # JSONに変換 (インデント付き)
            json_data = json.dumps(yaml_data, ensure_ascii=False, indent=2)
            # テキストエリアを更新
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, json_data)
            
            # 変換後に編集区切りを挿入
            self.text_area.edit_separator()
            self.last_content = json_data
            
            self.status_bar.config(text="YAMLからJSONに変換しました")
        except yaml.YAMLError as e:
            messagebox.showerror("エラー", f"YAMLの解析に失敗しました: {str(e)}")
        except Exception as e:
            messagebox.showerror("エラー", f"変換中にエラーが発生しました: {str(e)}")
    
    def format_json(self):
        content = self.text_area.get("1.0", tk.END+"-1c")
        if not content.strip():
            messagebox.showinfo("情報", "整形するテキストがありません")
            return
        
        try:
            # 変換前に編集区切りを挿入
            self.text_area.edit_separator()
            
            # JSONをパース
            json_data = json.loads(content)
            # 整形して出力 (インデント付き)
            formatted_json = json.dumps(json_data, ensure_ascii=False, indent=2)
            # テキストエリアを更新
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, formatted_json)
            
            # 変換後に編集区切りを挿入
            self.text_area.edit_separator()
            self.last_content = formatted_json
            
            self.status_bar.config(text="JSONを整形しました")
        except json.JSONDecodeError as e:
            messagebox.showerror("エラー", f"JSONの解析に失敗しました: {str(e)}")
        except Exception as e:
            messagebox.showerror("エラー", f"整形中にエラーが発生しました: {str(e)}")
    
    def format_yaml(self):
        content = self.text_area.get("1.0", tk.END+"-1c")
        if not content.strip():
            messagebox.showinfo("情報", "整形するテキストがありません")
            return
        
        try:
            # 変換前に編集区切りを挿入
            self.text_area.edit_separator()
            
            # YAMLをパース
            yaml_data = yaml.safe_load(content)
            # 整形して出力
            formatted_yaml = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
            # テキストエリアを更新
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, formatted_yaml)
            
            # 変換後に編集区切りを挿入
            self.text_area.edit_separator()
            self.last_content = formatted_yaml
            
            self.status_bar.config(text="YAMLを整形しました")
        except yaml.YAMLError as e:
            messagebox.showerror("エラー", f"YAMLの解析に失敗しました: {str(e)}")
        except Exception as e:
            messagebox.showerror("エラー", f"整形中にエラーが発生しました: {str(e)}")
    
    def show_help(self):
        help_text = """
JSON/YAMLコンバーターの使い方:

1. テキストエリアにJSONまたはYAMLデータを入力します。
2. 「JSON → YAML」または「YAML → JSON」ボタンをクリックするか、
   変換メニューから変換したい形式を選択します。
3. F5キーでJSON→YAML、F6キーでYAML→JSONに変換できます。
4. F7キーでJSONを整形、F8キーでYAMLを整形できます。

一般的なメモ帳としても使用できます。ファイルの新規作成、
開く、保存などの操作も可能です。
"""
        messagebox.showinfo("ヘルプ", help_text)
    
    def undo(self):
        """元に戻す機能"""
        try:
            # まず現在の編集状態を確定
            self.text_area.edit_separator()
            # 元に戻す操作を実行
            self.text_area.edit_undo()
            # 操作後の内容を記録
            self.last_content = self.text_area.get("1.0", tk.END+"-1c")
        except tk.TclError:
            # 元に戻せない場合は何もしない
            self.status_bar.config(text="これ以上元に戻せません")
    
    def redo(self):
        """やり直し機能"""
        try:
            # まず現在の編集状態を確定
            self.text_area.edit_separator()
            # やり直し操作を実行
            self.text_area.edit_redo()
            # 操作後の内容を記録
            self.last_content = self.text_area.get("1.0", tk.END+"-1c")
        except tk.TclError:
            # やり直しできない場合は何もしない
            self.status_bar.config(text="これ以上やり直せません")
    
    def show_about(self):
        messagebox.showinfo("このアプリについて", "JSON/YAML メモ帳 コンバーター\nバージョン 2.0\n\nJSON と YAML を簡単に相互変換できるテキストエディタです。\nメモ帳としての機能も備えています。")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONYAMLNotepad(root)
    root.mainloop()