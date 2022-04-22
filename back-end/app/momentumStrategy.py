import numpy as np
import pandas as pd
import xlsxwriter
from scipy.stats import percentileofscore as score
import requests
import math
from statistics import mean
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

stocks = pd.read_csv('sp_500_stocks.csv')

def momentumStrategy(portfolioSize, IEX_CLOUD_API_TOKEN, emailTo ):
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



    hqm_columns = [
        "Ticker",
        "Price",
        "Number of Shares to Buy",
        "One-Year Price Return",
        "One-Year Return Percentile",
        "Six-Month Price Return",
        "Six-Month Return Percentile",
        "Three-Month Price Return",
        "Three-Month Return Percentile",
        "One-Month Price Return",
        "One-Month Return Percentile",
        "HQM Score"
        ]

    hqm_dataframe = pd.DataFrame(columns = hqm_columns)

    for symbol_string in symbol_strings:
        url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(url).json()
        for symbol in symbol_string.split(","):
            try:
                hqm_dataframe = pd.concat([hqm_dataframe, pd.DataFrame({"Ticker": [symbol], "Price": [data[symbol]['price']],"Number of Shares to Buy": ["N/A"],"One-Year Price Return": [data[symbol]["stats"]['year1ChangePercent']],"One-Year Return Percentile": [0],"Six-Month Price Return": [data[symbol]["stats"]['month6ChangePercent']],"Six-Month Return Percentile": [0],"Three-Month Price Return" : [data[symbol]["stats"]['month3ChangePercent']],"Three-Month Return Percentile": [0],"One-Month Price Return": [data[symbol]["stats"]['month1ChangePercent']],"One-Month Return Percentile": [0], "HQM Score": [0]})],  ignore_index = True)
            except KeyError:
                print("error", symbol)

    timePeriods = ["One-Year", "Six-Month", "Three-Month", "One-Month"]
    for row in hqm_dataframe.index:
        for timePeriod in timePeriods:
            if hqm_dataframe.loc[row, f'{timePeriod} Price Return'] == None:
                hqm_dataframe.loc[row, f'{timePeriod} Price Return'] = 0
    for row in hqm_dataframe.index:
        for timePeriod in timePeriods:
            change_col = f'{timePeriod} Price Return'
            perc_col = f'{timePeriod} Return Percentile'
            hqm_dataframe.loc[row, perc_col] = (score(hqm_dataframe[change_col], hqm_dataframe.loc[row, change_col]) /100)


    for row in hqm_dataframe.index:
        momentumPerc = []
        for timePeriod in timePeriods:
            momentumPerc.append(hqm_dataframe.loc[row, f'{timePeriod} Return Percentile'])
        hqm_dataframe.loc[row, 'HQM Score'] = mean(momentumPerc)

    hqm_dataframe.sort_values('HQM Score', ascending = False, inplace = True)
    hqm_dataframe = hqm_dataframe[:50]
    hqm_dataframe.reset_index(inplace = True, drop = True)

    

    position_size = float(portfolioSize) / len(hqm_dataframe.index)
    for i in  hqm_dataframe.index:
        hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe.loc[i, 'Price'])


    writer = pd.ExcelWriter('momentum_strategy.xlsx', engine='xlsxwriter')
    hqm_dataframe.to_excel(writer, sheet_name = "Momentum Strategy", index = False)

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
                'num_format':'$0.00',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    integer_template = writer.book.add_format(
            {
                'num_format':'0',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    percent_template = writer.book.add_format(
            {
                'num_format':'00.0%',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )
    column_formats = {
        'A': ["Ticker", string_template],
        'B': ["Price", dollar_template],
        'C': ["Number of Shares to Buy", integer_template],
        'D': ["One-Year Price Return", percent_template],
        'E': ["One-Year Return Percentile", percent_template],
        'F': ["Six-Month Price Return", percent_template],
        'G': ["Six-Month Return Percentile", percent_template],
        'H': ["Three-Month Price Return", percent_template],
        'I': ["Three-Month Return Percentile", percent_template],
        'J': ["One-Month Price Return", percent_template],
        'K': ["One-Month Return Percentile", percent_template],
        'L': ["HQM Score", percent_template]
    }

    for column in column_formats.keys():
        writer.sheets['Momentum Strategy'].set_column( f'{column}:{column}', 25 , column_formats[column][1])
        writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0] , column_formats[column][1])

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
    emailMessage['Subject'] = f'Momentum Strategy Trades - {dateStr}'
    emailMessage.attach(MIMEText(html, 'html'))
    
    attachFileToEmail(emailMessage, 'momentum_strategy.xlsx')

    emailText = emailMessage.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(emailFrom, password)
        server.sendmail(emailFrom, emailTo, emailText)   


    return 'sucsess'