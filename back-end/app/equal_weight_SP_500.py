import pandas as pd
import requests
import numpy as np
import xlsxwriter
import math
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
def equalWeightSP500(portfolioSize, IEX_CLOUD_API_TOKEN, emailTo):        
    stocks = pd.read_csv('sp_500_stocks.csv')

    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


    #batch API call for stock info that places data in dataframe
    symbol_groups = list(chunks(stocks["Ticker"], 100))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))

    finalDataFrame = pd.DataFrame(columns = ["Ticker", "Stock Price", "Market Capitalization", "Number of Shares to Buy"])

    for symbol_string in symbol_strings:
        batchApiUrl = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batchApiUrl).json()
        for symbol in symbol_string.split(','):
            try: 
                finalDataFrame = pd.concat([finalDataFrame, pd.DataFrame({"Ticker": [symbol], "Stock Price": [data[symbol]['quote']['latestPrice']], "Market Capitalization": [data[symbol]['quote']['marketCap']], "Number of Shares to Buy": ["N/A"]})], ignore_index = True)
            except KeyError:
                print('error', symbol)

    # calculate number shares to buy from data and position
    val = float(portfolioSize)
    positionSize = val / len(finalDataFrame.index)
    for i in range(0, len(finalDataFrame.index)):
        finalDataFrame.loc[i, 'Number of Shares to Buy'] = math.floor(positionSize / finalDataFrame.loc[i, "Stock Price"])

    #outputs data to excel
    writer = pd.ExcelWriter('reccommended-trades.xlsx', engine = 'xlsxwriter')
    finalDataFrame.to_excel(writer, 'Reccommended Trades', index = False)

    backgroundColor = '#0a0a23'
    fontColor = '#ffffff'
    string_format = writer.book.add_format(
        {
            'font_color' : fontColor,
            'bg_color' : backgroundColor,
            'border': 1
        }
    )
    dollar_format = writer.book.add_format(
        {
            'num_format': '$0.00',
            'font_color' : fontColor,
            'bg_color' : backgroundColor,
            'border': 1
        }
    )
    integer_format = writer.book.add_format(
        {
            'num_format': '0',
            'font_color' : fontColor,
            'bg_color' : backgroundColor,
            'border': 1
        }
    )

    column_formats = {
        'A': ['Ticker', string_format],
        'B': ['Stock Price', dollar_format],
        'C': ['Market Capitalization', dollar_format],
        'D': ['Number of Shares to Buy', integer_format]
    }
    for column in column_formats.keys():
        writer.sheets['Reccommended Trades'].set_column(f'{column}:{column}', 18, column_formats[column][1])
        writer.sheets['Reccommended Trades'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

    writer.save()
    emailFrom = 'algotrading442@gmail.com'
    password = 'algotrade'
    html = '''
        <html>
            <body>
                <h1>This is a test</h1>
                <p>this is a test</p>
            </body>
        
        <html/>
        '''
    def attachFileToEmail(emailMessage, fileName):
        with open(fileName, 'rb') as f:
            file_attachment = MIMEApplication(f.read())

        file_attachment.add_header(
            "Content-Disposition",
            f'attachment; filename= {fileName}',
        )
        emailMessage.attach(file_attachment)

    dateStr = pd.Timestamp.today().strftime('%Y-%m-%d')
    emailMessage = MIMEMultipart()
    emailMessage['From'] = emailFrom
    emailMessage['To'] = emailTo
    emailMessage['Subject'] = f'Equal Weight S&P500 trades - {dateStr}'
    emailMessage.attach(MIMEText(html, 'html'))
    
    attachFileToEmail(emailMessage, 'reccommended-trades.xlsx')

    emailText = emailMessage.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(emailFrom, password)
        server.sendmail(emailFrom, emailTo, emailText)   

    return 'success'