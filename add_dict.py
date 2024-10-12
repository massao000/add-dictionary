import TkEasyGUI as eg
import unicodedata
from kanjize import number2kanji
import jaconv
import pykakasi
import re
import csv
from icecream import ic
import yaml
from pathlib import Path
from datetime import datetime

def is_lowercase_japanese(char):
    # Unicodeカテゴリが "Lo"（Letter, other）で拗音などの小さい文字を判定
    return unicodedata.name(char).startswith('HIRAGANA LETTER SMALL') or \
           unicodedata.name(char).startswith('KATAKANA LETTER SMALL')

def count_without_lowercase(s):
    '''小文字を覗いた文字数のカウントカウント
    ただし小文字の「っ」はカウントする
    '''
    # filtered_string = ''.join([char for char in s if not char.islower() and not is_lowercase_japanese(char)])
    # return len(filtered_string)
    count = 0
    for char in s:
        # 小文字の「っ」はカウントし、それ以外の小文字や小さい文字をスキップ
        if char == 'っ' or char == 'ッ' or (not char.islower() and not is_lowercase_japanese(char)):
            count += 1
    return count

def kanji2hiragana(text):
    '''カタカナをひらがなに変換する
    '''
    kks = pykakasi.kakasi()
    hiragana_text = ''.join([word['hira'] for word in kks.convert(text)])
    return hiragana_text

def numbers_to_kanji(text):
    '''数字を漢字に変換する
    '''
    # return number2kanji(int(text)) if text.isdigit() else text
    def replace_number(match):
        number = int(match.group())
        return number2kanji(number)
    
    return re.sub(r'\d+', replace_number, text)

# 全角変換
def fullwidth_conversion(text):
    
    return jaconv.h2z(text, ascii=True, digit=True)

# ひらがなをカタカナに変換し、ローマ字を全角に変換
def convert_text(text):
    # 数字を漢字に変換
    text_with_kanji_numbers = numbers_to_kanji(text)
    
    # ローマ字や半角英数字を全角に変換
    fullwidth_text = fullwidth_conversion(text_with_kanji_numbers)
    
    # 漢字をひらがなに変換
    hiragana_text = kanji2hiragana(fullwidth_text)
    
    # ひらがなをカタカナに変換
    katakana_text = jaconv.hira2kata(hiragana_text)
    
    return katakana_text


# CSVファイルを読み込む関数
def read_csv(file_path):
    with open(file_path, mode='r', newline="", encoding='utf-8') as f:
        reader = list(csv.reader(f))
    return reader

# CSVファイルとして保存する関数
def write_csv(file_path, matrix):
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(matrix)
    # ic(f"{file_path}に保存しました。")
    eg.popup_auto_close(f"{file_path}に保存しました。", auto_close_duration=2)

# CSVファイルの語尾に追記関数
def appending_csv(file_path, data):
    with open(file_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data)
    # ic(f"{file_path}に保存しました。")
    eg.popup_auto_close(f"{file_path}に保存しました。", auto_close_duration=2)

# CSVファイルから読み込んだデータを特定のインデックスで上書きする関数
def update_row_in_matrix(matrix, index, new_list, log_file):
    if 0 <= index < len(matrix):
        old_list = matrix[index]
        matrix[index] = new_list
        
        # 変更をログファイルに保存
        log_change(log_file, 'update', index, old_list, new_list)
    else:
        # ic("指定したインデックスが範囲外です。")
        eg.popup_error("指定したインデックスが範囲外です。")
    return matrix

# 指定したインデックスのリストを削除する関数
def remove_row_in_matrix(matrix, index, log_file):
    if 0 <= index < len(matrix):
        removed_list = matrix.pop(index)  # 指定したインデックスのリストを削除
        # 削除内容をログファイルに保存
        log_change(log_file, 'delete', index, removed_list)
    else:
        # ic("指定したインデックスが範囲外です。")
        eg.popup_error("指定したインデックスが範囲外です。")
    return matrix

# 上書き・削除のログを書き込む関数
def log_change(log_file, operation, index, old_list=None, new_list=None):
    with open(log_file, mode='a', encoding='utf-8') as file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if operation == 'update':
            file.write(f"[{timestamp}] Index {index} updated from {old_list} to {new_list}\n")
        elif operation == 'delete':
            file.write(f"[{timestamp}] Index {index} removed: {old_list}\n")
    # ic(f"ログファイル {log_file} に変更内容を保存しました。")
    eg.popup_auto_close(f"ログファイル {log_file} に変更内容を保存しました。", auto_close_duration=1)

# 入力のリセット
def input_reset(window):
    window['-WORD'].update('')
    window['-KANA_H'].update('')
    window['-KANA'].update('')
    window['-PRONUNCIATION_H'].update('')
    window['-PRONUNCIATION'].update('')
    window['-WORD_PRESET'].update('*')
    window['-COST'].update(1)
    window['-COST'].update(values=sorted(cost_choices))
    window['-POS'].update('名詞')
    window['-POS_SUBCATEGORY1'].update('固有名詞')
    window['-POS_SUBCATEGORY2'].update('一般')
    window['-POS_SUBCATEGORY3'].update('*')
    window['-CONJUGATION1'].update('*')
    window['-CONJUGATION2'].update('*')
    window['-ACCENT'].update(0)
    window['-STAR'].update('*')

with open('config.yaml', encoding="UTF-8") as f:
    yaml_data = yaml.safe_load(f)
    
system = yaml_data['system']

# コストやアクセントの場所、品詞などの選択肢を設定
# https://taku910.github.io/mecab/dic.html

cost_choices = yaml_data['cost_choices']  # 適宜変更可能
pos_choices = yaml_data['pos_choices']  # 品詞の選択肢
pos_type_choices = yaml_data['pos_type_choices']  # 品詞細分類
pos_type_choices2 = yaml_data['pos_type_choices2']  # 品詞細分類
pos_type_choices3 = yaml_data['pos_type_choices3']  # 品詞細分類
conjugation1 = yaml_data['conjugation1'] # 活用型
conjugation2 = yaml_data['conjugation2'] # 活用形


word_type_data = yaml_data['preset']
word_types = [i for i in word_type_data.keys()]

menu = [
    ['設定', ['保存/読み込み::DESTINATION', '確認::SETTING_CONFIRMATION']]
]

# レイアウト
layout1 = [
    [eg.Menu(menu)],
    [eg.Radio('追加', group_id='type', key='-RAD_ADD', enable_events=True, default=True), eg.Radio('編集', group_id='type', key='-RAD_UPDATE', enable_events=True, default=False), eg.Radio('削除', group_id='type', key='-RAD_DELETE', enable_events=True, default=False)],
    [eg.Checkbox('編集中でもカナ変換の有効化', default=False, key='-KANA_TRUE')],
    [eg.Text('単語', size=(15, 1)), eg.InputText(key='-WORD', expand_x=True, enable_events=True)],
    [eg.Text('読み編集', size=(15, 1)), eg.InputText(key='-KANA_H', expand_x=True, enable_events=True)],
    [eg.Text('読み（カタカナ）', size=(15, 1)), eg.InputText(key='-KANA', expand_x=True, enable_events=True, readonly=True)],
    [eg.Text('発音編集', size=(15, 1)), eg.InputText(key='-PRONUNCIATION_H', expand_x=True, enable_events=True)],
    [eg.Text('発音（カタカナ）', size=(15, 1)), eg.InputText(key='-PRONUNCIATION', expand_x=True, enable_events=True, readonly=True)],
    [eg.Text('プリセット', size=(15, 1)), eg.Combo(word_types, key='-WORD_PRESET', default_value='*', enable_events=True)],
    [eg.Text('コスト', size=(15, 1)), eg.Combo(sorted(cost_choices), default_value=1, key='-COST')],
    [eg.Text('品詞', size=(15, 1)), eg.Combo(pos_choices, default_value='名詞', key='-POS')],
    [eg.Text('品詞細分類1', size=(15, 1)), eg.Combo(pos_type_choices, default_value='固有名詞', key='-POS_SUBCATEGORY1')],
    [eg.Text('品詞細分類2', size=(15, 1)), eg.Combo(pos_type_choices2, default_value='一般', key='-POS_SUBCATEGORY2')],
    [eg.Text('品詞細分類3', size=(15, 1)), eg.Combo(pos_type_choices3, default_value='*', key='-POS_SUBCATEGORY3')],
    [eg.Text('活用型', size=(15, 1)), eg.Combo(conjugation1, default_value='*', key='-CONJUGATION1')],
    [eg.Text('活用形', size=(15, 1)), eg.Combo(conjugation2, default_value='*', key='-CONJUGATION2')],
    [eg.Text('アクセント', size=(15, 1)), eg.Combo([], default_value=0, key='-ACCENT')],
    [eg.Text('アクセント結合規則', size=(15, 1)), eg.Combo(['*',"C1","C2","C3","C4","C5",], key='-STAR', default_value='*')],
    [eg.Button('追加', color='blue', key='-CSV-', disabled=False), eg.Button('更新', key='-DICT_UP-', disabled=True), eg.Button('削除', key='-DICT_DELETE-', disabled=True), eg.Button('初期化', color='blue', key='-RESET-')]
]

if not system['save_csv_path'] is None:
    csv_filename = Path(system['save_csv_path'])
    if csv_filename.is_file():
        reader = read_csv(csv_filename)
    else:
        reader = []
else:
    reader = []

headings = ['表層形','左文脈ID','右文脈ID','コスト','品詞','品詞細分類1','品詞細分類2','品詞細分類3','活用型','活用形','原形','読み','発音', 'アクセント', 'アクセント結合規則']
# 列の幅
widths=[10,5,5,4,5,6,6,6,5,4,10,10,10,5,5]

layout2 = [
    [eg.Table(reader, headings, col_widths=widths, key='-TABLE_DATA', justification='left', enable_events=True, expand_y=True, expand_x=True)]
]

col1 = eg.Column(layout1, key="col1", expand_y=True, expand_x=True)
col2 = eg.Column(layout2, key="col2", expand_y=True, expand_x=True)

layout = [
    [col1, eg.VSeparator(pad=0, size=(0, 0)), col2]
]

# ウィンドウを作成
# window = eg.Window('辞書作成', layout, keep_on_top=True)
window = eg.Window('辞書作成', layout, resizable=True)

log_file_path = 'add_dict_changes.log'

table_index = 0
# イベントループ
while True:
    event, values = window.read()

    if event == eg.WIN_CLOSED or event == '-EXIT-':
        break
    
    # ic(values)
    
    if '-RAD_' in event:
        try:
            if values['-RAD_ADD'] == True:
                window['-CSV-'].update(color='blue', disabled=False)
                window['-DICT_UP-'].update(disabled=True)
                window['-DICT_DELETE-'].update(disabled=True)
            elif values['-RAD_UPDATE'] == True:
                window['-CSV-'].update(disabled=True)
                window['-DICT_UP-'].update(color='blue', disabled=False)
                window['-DICT_DELETE-'].update(disabled=True)
            elif values['-RAD_DELETE'] == True:
                window['-CSV-'].update(disabled=True)
                window['-DICT_UP-'].update(disabled=True)
                window['-DICT_DELETE-'].update(color='blue', disabled=False)
        except:
            pass
    
    # 保存先の設定
    if event == 'DESTINATION':
        csv_filename = eg.popup_get_file('保存先に設定する辞書ファイルを選択', file_types=(('csv files', '.csv'),))
        if csv_filename:
            # ic(csv_filename)
            # system['save_csv_path'] = csv_filename
            yaml_data['system']['save_csv_path'] = csv_filename
            
            with open('config.yaml', 'w', encoding="UTF-8") as f:
                yaml.dump(yaml_data, f, allow_unicode=True)
            
            reader = read_csv(csv_filename)
            window['-TABLE_DATA'].update(values=reader)
    
    if event == 'SETTING_CONFIRMATION':
        eg.popup(f"保存/書き込みファイルパス：{system['save_csv_path']}", "設定内容の確認")
        
    # テーブルデータをクリックしたときに入力フォームに記述する
    if event == '-TABLE_DATA':
        try:
            if values['-TABLE_DATA']:
                table_index = values['-TABLE_DATA'][-1]
            else:
                continue
                
            data = reader[table_index]
            
            pattern = r"(\d+)/"
            match = re.search(pattern, data[13])
            
            window['-WORD'].update(data[0])
            window['-KANA_H'].update(data[11])
            window['-KANA'].update(data[11])
            window['-COST'].update(data[3])
            window['-POS'].update(data[4])
            window['-POS_SUBCATEGORY1'].update(data[5])
            window['-POS_SUBCATEGORY2'].update(data[6])
            window['-POS_SUBCATEGORY3'].update(data[7])
            window['-CONJUGATION1'].update(data[8])
            window['-CONJUGATION2'].update(data[9])
            window['-ACCENT'].update(match.group(1))
            window['-STAR'].update(data[14])
        except:
            eg.popup_error('何らかのエラー')

    # プリセットの選択したときの入力フォームに記述されるもの
    if event == '-WORD_PRESET':
        # ic(word_type_data[values['-WORD_PRESET']])
        x = word_type_data[values['-WORD_PRESET']]
        window['-COST'].update(x['cost_candidates'][0])
        window['-COST'].update(values=x['cost_candidates'])
        window['-POS'].update(x['part_of_speech'])
        window['-POS_SUBCATEGORY1'].update(x['part_of_speech_detail_1'])
        window['-POS_SUBCATEGORY2'].update(x['part_of_speech_detail_2'])
        window['-POS_SUBCATEGORY3'].update(x['part_of_speech_detail_3'])
    
    # 単語が入力された際に実行
    # 単語をカタカナに変換する
    if event == '-WORD':
        if values['-RAD_ADD'] or values['-KANA_TRUE']:
            text = convert_text(values['-WORD'])
            window['-KANA'].update(text)
            window['-KANA_H'].update(text)
            window['-PRONUNCIATION'].update(text)
            window['-PRONUNCIATION_H'].update(text)
    
    # 読み、発音編集
    if event == '-KANA_H':
        window['-KANA'].update(convert_text(values['-KANA_H']))
        window['-PRONUNCIATION_H'].update(convert_text(values['-KANA_H']))
        window['-PRONUNCIATION'].update(convert_text(values['-KANA_H']))
        
    # 発音編集
    if event == '-PRONUNCIATION_H':
        window['-PRONUNCIATION'].update(convert_text(values['-PRONUNCIATION_H']))
    
    # 文字数のカウント
    if event == '-KANA':
        window['-ACCENT'].update(0)
        window['-ACCENT'].update(values=list(range(0, count_without_lowercase(values['-KANA']) + 1)))
        
    # 辞書の追記k
    if event == '-CSV-':
        
        if not values["-WORD"]:
            eg.popup_error('単語が入力されていません')
            continue
        if not values["-KANA"]:
            eg.popup_error('読み方が入力されていません')
            continue
        if not values["-COST"]:
            eg.popup_error('コストが入力されていません')
            continue
        
        if not system['save_csv_path']:
            eg.popup_error('保存先が指定されていません\n設定から「保存/読み込み」先を選択してください')
            continue
        
        
        # 重複の確認
        reader = read_csv(csv_filename)
        for i in reader:
            if i[0] == values["-WORD"] and i[11] == values["-KANA"]:
                eg.popup_error('単語と読みが辞書データと重複しています')
                break
        else:
            if csv_filename:
                data = [
                    values["-WORD"],
                    '',
                    '',
                    values["-COST"],
                    values["-POS"],
                    values["-POS_SUBCATEGORY1"],
                    values["-POS_SUBCATEGORY2"],
                    values["-POS_SUBCATEGORY3"],
                    values["-CONJUGATION1"],
                    values["-CONJUGATION2"],
                    fullwidth_conversion(values["-WORD"]),
                    values["-KANA"],
                    values["-PRONUNCIATION"],
                    f'{values["-ACCENT"]}/{count_without_lowercase(values["-KANA"])}',
                    values["-STAR"]]
                appending_csv(csv_filename, data)
                    
                reader = read_csv(csv_filename)
                window['-TABLE_DATA'].update(values=reader)
    
    # 辞書の書き換え
    if event == '-DICT_UP-' and values['-RAD_UPDATE']:
        try:
            if values['-TABLE_DATA']:
                table_index = values['-TABLE_DATA'][-1]
            else:
                continue
                
            # ic(table_index)
            if table_index:
                data = [
                    values["-WORD"],
                    '',
                    '',
                    values["-COST"],
                    values["-POS"],
                    values["-POS_SUBCATEGORY1"],
                    values["-POS_SUBCATEGORY2"],
                    values["-POS_SUBCATEGORY3"],
                    values["-CONJUGATION1"],
                    values["-CONJUGATION2"],
                    fullwidth_conversion(values["-WORD"]),
                    values["-KANA"],
                    values["-PRONUNCIATION"],
                    f'{values["-ACCENT"]}/{count_without_lowercase(values["-KANA"])}',
                    values["-STAR"]]
                
                matrix = update_row_in_matrix(reader, table_index, data, log_file_path)
                
                # 更新後のデータを再びCSVファイルとして保存
                output_csv_file_path = yaml_data['system']['save_csv_path']
                write_csv(output_csv_file_path, matrix)
                
                reader = read_csv(csv_filename)
                window['-TABLE_DATA'].update(values=reader)
                
                input_reset(window)
        except:
            eg.popup_error("テーブルから選択してください")

    # 辞書の削除
    if event == '-DICT_DELETE-' and values['-RAD_DELETE']:
        try:
            if values['-TABLE_DATA']:
                table_index = values['-TABLE_DATA'][-1]
            else:
                continue
            
            # ic(table_index)
            if table_index:
                matrix = remove_row_in_matrix(reader, table_index, log_file_path)
                
                # 更新後のデータを再びCSVファイルとして保存
                output_csv_file_path = yaml_data['system']['save_csv_path']
                write_csv(output_csv_file_path, matrix)
                
                reader = read_csv(csv_filename)
                window['-TABLE_DATA'].update(values=reader)
                
                input_reset(window)
        except:
            eg.popup_error("2テーブルから選択してください")
            
    if event == '-RESET-':
        input_reset(window)
    
window.close()
