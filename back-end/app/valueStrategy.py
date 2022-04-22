import numpy as np
import pandas as pd
import xlsxwriter
import requests
from scipy.stats import percentileofscore as score
import math
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication



def valueStrategy(portfolio_size, IEX_CLOUD_API_TOKEN, emailTo):
    stocks = pd.read_csv('sp_500_stocks.csv')

    # Function sourced from 
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]   
            
    symbol_groups = list(chunks(stocks['Ticker'], 100))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))
    #     print(symbol_strings[i])

    def portfolio_input():
        global portfolio_size
        portfolio_size = input("Enter the value of your portfolio:")

        try:
            val = float(portfolio_size)
        except ValueError:
            print("That's not a number! \n Try again:")
            portfolio_size = input("Enter the value of your portfolio: ")

    my_columns = [
        "Ticker",
        "Price",
        "Number of Shares to Buy",
        "Price-to-Earnings Ratio",
        "PE Percentile",
        "Price-to-Book Ratio",
        "PB Percentile",
        "Price-to-Sales Ratio",
        "PS Percentile",
        "EV/EBITDA",
        "EV/EBITDA Percentile",
        "EV/GP",
        "EV/GP Percentile",
        "RV Score"
        ]
    RVDataframe = pd.DataFrame(columns = my_columns)
    for symbolString in symbol_strings:
        data = url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbolString}&types=quote,advanced-stats&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(url).json()
        for symbol in symbolString.split(','):
            try:
                eeRatio = (data[symbol]['advanced-stats']['enterpriseValue'] / data[symbol]['advanced-stats']['EBITDA'])
            except TypeError:
                eeRatio = np.NaN
            try:
                egRatio = (data[symbol]['advanced-stats']['enterpriseValue'] / data[symbol]['advanced-stats']['grossProfit'])
            except TypeError:
                egRatio = np.NaN
            RVDataframe = pd.concat([RVDataframe, pd.DataFrame({"Ticker": [symbol], "Price": [data[symbol]['quote']['latestPrice']], "Number of Shares to Buy": ["N/A"], "Price-to-Earnings Ratio": [data[symbol]['quote']['peRatio']], "PE Percentile": ["N/A"], "Price-to-Book Ratio": [data[symbol]['advanced-stats']['priceToBook']], "PB Percentile": ["N/A"], "Price-to-Sales Ratio": [data[symbol]['advanced-stats']['priceToSales']], "PS Percentile": ["N/A"], "EV/EBITDA": [eeRatio], "EV/EBITDA Percentile": ['N/A'], "EV/GP": [egRatio],"EV/GP Percentile": ['N/A'], "RV Score": ["N/A"] })], ignore_index= True)

    for column in ["Price-to-Earnings Ratio", "Price-to-Book Ratio", "Price-to-Sales Ratio", "EV/EBITDA", "EV/GP"]:
        RVDataframe[column].fillna(RVDataframe[column].mean(), inplace=True)


    metrics = {
        "Price-to-Earnings Ratio": "PE Percentile",
        "Price-to-Book Ratio": "PB Percentile",
        "Price-to-Sales Ratio": "PS Percentile",
        "EV/EBITDA": "EV/EBITDA Percentile",
        "EV/GP": "EV/GP Percentile"
    }

    for metric in metrics.keys():
        for row in RVDataframe.index:
            RVDataframe.loc[row, metrics[metric]] = (score(RVDataframe[metric], RVDataframe.loc[row, metric]) / 100) 
    from statistics import mean

    for row in RVDataframe.index:
        RVDataframe.loc[row, "RV Score"] = (mean([RVDataframe.loc[row, "PE Percentile"], RVDataframe.loc[row, "PB Percentile"], RVDataframe.loc[row, "PS Percentile"], RVDataframe.loc[row, "EV/EBITDA Percentile"], RVDataframe.loc[row, "EV/GP Percentile"]]) * 100)


    RVDataframe.sort_values("RV Score", ascending=True, inplace=True)
    RVDataframe = RVDataframe[:50]
    RVDataframe.reset_index(drop=True, inplace = True)


    

    for row in RVDataframe.index:
        RVDataframe.loc[row, 'Number of Shares to Buy'] = math.floor((float(portfolio_size) / len(RVDataframe.index)) / RVDataframe.loc[row, 'Price'])

    writer = pd.ExcelWriter('value_strategy.xlsx', engine = 'xlsxwriter')
    RVDataframe.to_excel(writer, 'Value Strategy', index = False)

    background_color = '#0a0a23'
    font_color = '#ffffff'

    string_template = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
    dollar_template = writer.book.add_format(
        {
            'num_format': '$0.00',
            'font_color':font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
    integer_template = writer.book.add_format(
        {
            'num_format': '0',
            'font_color':font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
    float_template = writer.book.add_format(
        {
            'num_format': '0.0',
            'font_color':font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
    percent_template = writer.book.add_format(
        {
            'num_format': '0.0%',
            'font_color':font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

    column_format = {
        'A': ["Ticker", string_template],
        'B': ["Price", dollar_template],
        'C': ["Number of Shares to Buy", integer_template],
        'D': ["Price-to-Earnings Ratio", float_template],
        'E': ["PE Percentile", percent_template],
        'F': ["Price-to-Book Ratio", float_template],
        'G': ["PB Percentile", percent_template],
        'H': ["Price-to-Sales Ratio", float_template],
        'I': ["PS Percentile", percent_template],
        'J': ["EV/EBITDA", float_template],
        'K': ["EV/EBITDA Percentile", percent_template],
        'L': ["EV/GP", float_template],
        'M': ["EV/GP Percentile", percent_template],
        'N': ["RV Score", string_template]
    }
    for column in column_format.keys():
        writer.sheets['Value Strategy'].set_column(f'{column}:{column}', 25, column_format[column][1])
        writer.sheets['Value Strategy'].write(f'{column}1', column_format[column][0], string_template)
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
    emailMessage['Subject'] = f'Value Strategy Trades - {dateStr}'
    emailMessage.attach(MIMEText(html, 'html'))
    
    attachFileToEmail(emailMessage, 'value_strategy.xlsx')

    emailText = emailMessage.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(emailFrom, password)
        server.sendmail(emailFrom, emailTo, emailText)   

    return 'success'