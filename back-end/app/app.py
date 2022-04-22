from flask import Flask
from requests import request
from equal_weight_SP_500 import equalWeightSP500
from momentumStrategy import momentumStrategy
from secrety import IEX_CLOUD_API_TOKEN
from valueStrategy import valueStrategy
from flask import request
app = Flask(__name__)



@app.route("/SP500", methods=['GET','POST'])
def SP500():
    portfolioSize = request.args.get('portfolioSize')
    emailTo = request.args.get('emailTo')
    return equalWeightSP500(portfolioSize, IEX_CLOUD_API_TOKEN, emailTo)


@app.route("/momentum", methods=['GET','POST'])
def Momentum():
    portfolioSize = request.args.get('portfolioSize')
    emailTo = request.args.get('emailTo')
    return momentumStrategy(portfolioSize, IEX_CLOUD_API_TOKEN, emailTo)


@app.route("/value", methods=['GET','POST'])
def Value():
    portfolioSize = request.args.get('portfolioSize')
    emailTo = request.args.get('emailTo')
    return valueStrategy(portfolioSize, IEX_CLOUD_API_TOKEN, emailTo)