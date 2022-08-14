# pip install pillow
# pip install pytesseract
# brew install 
import sys
print(sys.executable)

from PIL import Image
import os
from pytesseract import pytesseract
import math
import pandas as pd

pd.options.display.float_format = '{:,.2f}'.format

# path to folder containing the image
files = os.listdir("/Users/gaurav/Desktop/Coding/Split-Bill")

# find path to image in the folder being used
def find_image_path(files):
    for file in files:
        if file[-4:]=="jpeg":
            image_path = file
            
    return image_path

#split the text into a list by line break
def split_by_line(text):
    content = []
    ctr = 0
    prev_pos = 0
    for i in range(len(text)):
        if text[i] == '\n':
            content.append(text[prev_pos+1:i])
            ctr = ctr + 1
            prev_pos = i
    content = list(filter(None, content))
    return content

#Find Index that contains a string
def find_index_of_string(text, string):
    index = [i for i, s in enumerate(text) if string in s][0]
    return index

#get price from line on reciept
def get_price(money):
    money = float(money.split('$')[1])
    return money

#find index of list where the items begin
def find_start_of_items(text, index, sub_total):
    total = []
    for num in reversed(range(index)):
        total.append(float(text[num].split('$')[1]))
        if "{:.2f}".format((math.fsum(total))) == "{:.2f}".format(sub_total):
            start = num
            break
    
    return start

# make main dishes into pandas dataframe
def main_dishes_pandas (text, start,index_sub_total):
    items = text[start:index_sub_total]
    number_of_items = []
    dish = []
    cost = []
    
    for item in items:
        number_of_items.append(item[0])
        name = item.split('$')[0]
        dish.append(name[1:])
        cost.append(float(item.split('$')[1]))
        
    df = pd.DataFrame({'num':number_of_items,'dish': dish,'cost':cost})
    return df

  # asks user to input who ordered what
def who_ordered_what(df):
    names= []
    for index, row in df.iterrows():
        for num in row.num:
            names.append(input('Who ordered' + row.dish + 'for ' +"{:.2f}: ".format(row.cost) )+ ' ')
    df['name'] = names
    
    return df

#handles multiple orders by same user
def handling_duplicate_names(df):
    df['total'] = df.groupby(['name'])['cost'].transform('sum')
    df = df.drop_duplicates(subset='name')
    df = df[['name','total']]
    return df

# gets the total of additional taxes
def get_tax_total(text, sub_total):  
    Total_index = find_index_of_string(text,'Total')
    total = get_price(text[Total_index])
    tax = total - sub_total
    return tax

#formats a pandas receipt for each individual
def format_receipt(df,tax): 
    print('\n')
    taxes = list()
    for index, row in df.iterrows():
        percentage = (row.total/sum(df.total))
        taxes.append(percentage*tax)
    df["taxes"] = taxes
    df["to_pay"] = (df["taxes"] + df["total"])
    # df = df.pivot_table(index='name',
    #                margins=True,
    #                margins_name='total',  # defaults to 'All'
    #                aggfunc=sum)
    row_sum = df.iloc[:,1:4].sum()
    df.loc['Total'] = row_sum
    df.fillna('')
    
    return df

def format_message(df):
    print('\n')
    for index, row in df.iterrows():
        print(str(row["name"])+ ' owes $'+ "{:.2f}".format(row.to_pay))
        if index == len(df.index) - 1:
            break



#Open image with PIL
img = Image.open(find_image_path(files))

#Extract text from image
text = pytesseract.image_to_string(img,config ='--psm 6 --oem 3')

text = split_by_line(text)
index_sub_total = find_index_of_string(text,'Subtotal')
sub_total = get_price(text[index_sub_total])
start = find_start_of_items(text, index_sub_total, sub_total)

df =  main_dishes_pandas(text, start,index_sub_total)

df = who_ordered_what(df)

df = handling_duplicate_names(df)

tax = get_tax_total(text,sub_total)
df = format_receipt(df,tax)
print(df)

format_message(df)