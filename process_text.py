# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
from datetime import date
import os
import re
import unicodedata as ud

# %%
def get_id(bn):
    ids = re.findall(r'BN\w+-BN\w+|BN\w+',bn)
    ids = [i.replace('BN','') for i in ids]

    id_list = []
    for i in ids:
        numeric_ids = i.split('-')
        if len(numeric_ids)==2:
            id_list += list(np.arange(int(numeric_ids[0]),int(numeric_ids[1])+1))
        else:
            id_list.append(int(numeric_ids[0]))
    # Phòng việc nhầm mã với BN F0 (ví dụ: 'F1 của BN69'), thì chỉ nhận số bệnh nhân theo thứ tự tăng dần, 
    # vì chắc chắc không ai liệt kê kiểu đi lùi hay 'bn50 là f1 của bn49' cả
    return [id_list[0]]+[id_list[i] for i in range(1,len(id_list)) if id_list[i-1]<id_list[i]]


# %%
# nếu từ nam với nữ trùng địa danh (Hà Nam, Nữ Oa,...), việc chỉ lọc chữ thường sẽ giúp bỏ được các trường hợp trên 
get_sex = lambda bn: 'Nữ' if 'nữ' in bn else 'Nam' if 'nam' in bn else np.nan

def get_age(bn):
    kw = re.findall(r'[0-9]+ tuổi',bn)
    if not kw:
        return np.nan
    return re.search(r'[0-9]+',kw[0]).group()
    
get_cbyt = lambda bn: int('cán bộ y tế' in bn or 'nhân viên y tế' in bn.lower())


# %%
def get_location(don_vi_hanh_chinh, bn):
    regex_loc = re.compile('|'.join([kw.upper()+' (.*?)'+stop for kw in ['địa chỉ'] for stop in ['\\.',';',':']]))
    loc_array = re.findall(regex_loc, bn.upper())
    if not loc_array:
        return np.nan 
    bn_loc = ''.join(loc_array[0])+'.'

    regex = re.compile('|'.join([don_vi_hanh_chinh.upper()+' (.*?)'+stop for stop in [',','\\.',';',':']]))
    # Nếu ghi nhận 2 địa điểm thì chọn địa điểm đầu, vì sẽ nêu địa chỉ trước lịch sử di chuyển
    loc_array = re.findall(regex, bn_loc)
    if not loc_array:
        return np.nan 
    loc_text = ''.join(loc_array[0])
    loc = re.split(r';|,|\.|:',loc_text)
    return loc[0]


# %%
def get_quoctich(bn):
    regex = re.compile('|'.join(['quốc tịch'+' (.*?)'+stop for stop in [',','\\.',';',':']]))
    loc_array = re.findall(regex, bn.lower())
    if not loc_array:
        return 'Việt Nam' 
    loc_text = ''.join(loc_array[0])
    loc = re.split(r';|,|\.|:',loc_text)
    return loc[0]
#get_quoctich()


# %%
def get_cluster_source(bn):
    if 'điều trị tại Bệnh viện Bệnh nhiệt đới Trung ương cơ sở Đông Anh'.lower() not in bn.lower() and 'nhiệt đới Trung ương cơ sở Đông Anh'.lower() in bn.lower():
        return 'Bệnh viện Bệnh nhiệt đới Trung ương cơ sở Đông Anh', 'BV'
    elif 'nhập cảnh'.lower() in bn.lower():
        return 'Nhập cảnh','Nhập cảnh'
    regex = re.compile('|'.join([kw+' (.*?)'+stop for kw in ['F1',ud.normalize('NFC','Ổ DỊCH')] for stop in [',','\\.',';',':']]))
    loc_array = re.findall(regex, ud.normalize('NFC',bn.upper()))
    if not loc_array:
        return np.nan, np.nan
    loc_text = ''.join(loc_array[0])
    loc = re.split(r';|,|\.|:',loc_text)[0]
    normalized_loc = ud.normalize('NFC',loc)
    rm_words = [ud.normalize('NFC',w) for w in ['CỦA ','VỚI ','LIÊN QUAN ', 'TỚI ', 'ĐẾN ', ' TRƯỚC ĐÓ']]
    for w in rm_words:
        normalized_loc = normalized_loc.replace(w,'') 
    return normalized_loc,'Tiếp xúc gần/Đi qua vùng dịch'

get_group = lambda bn: 'Nhập cảnh' if 'nhập cảnh'.lower() in bn.lower() else 'CỘng đồng'


# %%
def get_dieutri(bn):
    regex = re.compile('|'.join(['điều trị tại'+' (.*?)'+stop for stop in [',','\\.',';',':']]))
    loc_array = re.findall(regex, bn)
    if not loc_array:
        return np.nan
    loc_text = ''.join(loc_array[0])
    loc = re.split(r';|,|\.|:',loc_text)
    return loc[0]

# %%
def add_patient_info(bn, date = date.today().strftime('%d/%m/%Y')):
    code = get_id(bn)
    sex = get_sex(bn)
    age = get_age(bn)
    cbyt = get_cbyt(bn)

    thon = get_location('thôn',bn)
    if pd.isnull(thon):
        thon = get_location('ấp',bn)

    phuong = get_location('phường',bn)
    if pd.isnull(phuong):
        phuong = get_location('xã',bn)

    huyen = get_location('huyện',bn)
    if pd.isnull(huyen):
        huyen = get_location('quận',bn)

    tp = get_location('thành phố',bn)
    if pd.isnull(tp):
        tp = get_location('tỉnh',bn)

    quoctich = get_quoctich(bn)
    cluster,source = get_cluster_source(bn)
    dieutri = get_dieutri(bn)
    group = get_group(bn)

    return [{'PatientCode':c, 'Giời tính':sex, 'Tuổi':age, 'CBYT':cbyt,
             'Thôn/Ấp':thon, 'Xã/Phường':phuong, 'Quận/Huyện':huyen, 'TP/Tỉnh':tp, 
             'Quốc tịch':quoctich, 'Cluster':cluster, 'Nguồn lây':source,
             'Ngày thông báo':date, 'Nơi điều trị':dieutri, 'Nhóm':group} for c in code]


# %%
def process_bn(text_file, output = 'output.csv', date = date.today().strftime('%d/%m/%Y')):
    with open(text_file,'r',encoding='utf8') as file:
        text = ud.normalize('NFC',file.read()).split('\n')

    script1 = [bn for bn in text if 'ca bệnh' in bn[:15].lower()]

    rows=[]
    for bn in script1:
        rows += add_patient_info(bn,date)

    df_out = pd.DataFrame(rows)
    df_out.to_csv(output,index=False)

def main():
    input_file = input('Nhập tên file text của bạn vào đây (ví dụ: 1205.txt): ')
    day = input('Nhập ngày thông báo ca bệnh. Bấm Enter sẽ lấy ngày hôm nay là ngày công bố: ')
    if day:
        process_bn(input_file,input_file.replace('.txt','.csv'),day)
    else:
        process_bn(input_file,input_file.replace('.txt','.csv'))


if __name__ == "__main__":
    main()