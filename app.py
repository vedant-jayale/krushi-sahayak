from flask import Flask, render_template, request,make_response

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Mapping dictionary for header translations
header_translations = {
   'Sl no.':'क्र.',
    'Commodity': 'धान्य / फसल',
    'District Name':'जिल्हा',
    'Market Name':'बाजार(Market)',

    'Variety': 'प्रकार',
    'Grade': 'गुणवत्ता',
    'Min Price (Rs./Quintal)': 'किमत प्रति क्विंटल(₹) (किमान))',
    'Max Price (Rs./Quintal)': 'किमत प्रति क्विंटल(₹) (कमाल))',
    'Modal Price (Rs./Quintal)': 'सरासरी किमत(₹) (प्रति क्विंटल )',
    'Price Date': 'किमत तारीख'
}

# Function to translate headers
def translate_header(header):
    return header_translations.get(header, header)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')

@app.route('/sahayata')
def sahayata():
    return render_template('sahayata.html')

@app.route('/havaman')
def havaman():
    return render_template('havaman.html')

@app.route('/kapusvyavasthapan')
def kapusvyavasthapan():
    return render_template('kapusvyavasthapan.html')

@app.route('/soil-testing')
def soiltesting():
    return render_template('soil-testing.html')


@app.route('/get_prices', methods=['GET', 'POST'])
def get_prices():
    data = None
    form_submitted = False
    if request.method == 'POST':
        form_submitted = True
        commodity = request.form['commodity']
        state = request.form['state']
        district = request.form['district']
        market = request.form['market']
        date_from = request.form['date_from']
        date_to = request.form['date_to']

        commodity_name = request.form['commodity_name']
        state_name = request.form['state_name']
        district_name = request.form['district_name']
        market_name = request.form['market_name']

        url = (f"https://agmarknet.gov.in/SearchCmmMkt.aspx?"
               f"Tx_Commodity={commodity}&Tx_State={state}&Tx_District={district}&Tx_Market={market}"
               f"&DateFrom={date_from}&DateTo={date_to}&Fr_Date={date_from}&To_Date={date_to}&Tx_Trend=0"
               f"&Tx_CommodityHead={commodity_name}&Tx_StateHead={state_name}&Tx_DistrictHead={district_name}&Tx_MarketHead={market_name}")

        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

       
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Parsing logic to extract data from the page
        data = []
        table = soup.find('table', {'class': 'tableagmark_new'})
        if table:
            print("Table found")
            headers = [translate_header(header.text.strip()) for header in table.find_all('th')]
            print("Headers:", headers)
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                cols = [col.text.strip() for col in cols]
                if 'No Data Found' in cols:
                    data = None
                    break
                data.append(dict(zip(headers, cols)))
                
        else:
            print("No table found")
            # If no table is found, return None or empty data
            data = None      

    return render_template('index.html', data=data, form_submitted=form_submitted)


if __name__ == '__main__':
    app.run(debug=True)
