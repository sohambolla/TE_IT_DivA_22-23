from flask import Flask,render_template,url_for,request,jsonify
from flask_cors import cross_origin

import pandas as pd
import numpy as np
import datetime
import pickle


app = Flask(__name__, template_folder="template")
model = pickle.load(open('catfm.pkl', 'rb'))



@app.route('/',methods=['GET'])
@cross_origin()
def home():
    return render_template("index.html")

@app.route('/prediction', methods=['GET', 'POST'])
@cross_origin()
def predict():
    if request.method ==  'POST':
        Gender = float(request.form['Gender'])
        Married = float(request.form['Married'])
        Dependents = float(request.form['Dependents'])
        Education = float(request.form['Education'])
        Employed = float(request.form['Employed'])
        Credit_History = float(request.form['Credit_History'])
        Property_Area = float(request.form['Property_Area'])
        ApplicantIncome = float(request.form['ApplicantIncome'])
        CoapplicantIncome = float(request.form['CoapplicantIncome'])
        LoanAmount = int(request.form['LoanAmount'])
        Loan_Amount_Term = int(request.form['Loan_Amount_Term'])
        if LoanAmount == 0 or Loan_Amount_Term <= 12 or Credit_History == 0 :
            return render_template("noform.html")
        else:
            prediction = model.predict([[Gender,Married,Dependents,Education,Employed,Credit_History,Property_Area,ApplicantIncome,CoapplicantIncome,LoanAmount,Loan_Amount_Term]])
            output = prediction
            if output == 0:
                return render_template("noform.html")
            else:
                return render_template("form.html")
    return render_template("loan_prediction.html")


@app.route ('/home1')
def home1 (): 
    return render_template ('calculation.html')
@app.route ('/home2')
def home2 (): 
    return render_template ('./sample.html')

if __name__ == "__main__":
    app.run(debug=True)