from flask import Flask, render_template, request,make_response

import requests
from bs4 import BeautifulSoup
import logging

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
logging.basicConfig(level=logging.DEBUG)   

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

        # Construct the URL for Agmarknet with the parameters
        url = (f"https://agmarknet.gov.in/SearchCmmMkt.aspx?"
               f"Tx_Commodity={commodity}&Tx_State={state}&Tx_District={district}&Tx_Market={market}"
               f"&DateFrom={date_from}&DateTo={date_to}&Fr_Date={date_from}&To_Date={date_to}&Tx_Trend=0"
               f"&Tx_CommodityHead={commodity_name}&Tx_StateHead={state_name}&Tx_DistrictHead={district_name}&Tx_MarketHead={market_name}")

        # Scraper API URL with your API key
        scraper_api_url = f"http://api.scraperapi.com?api_key=abbd392168a5681912e35e5698f9db14&url={url}"

        try:
            logging.debug(f"Sending request to Scraper API: {scraper_api_url}")
            # Make the request to Scraper API with timeout and retries
            response = requests.get(scraper_api_url, timeout=40)
            response.raise_for_status()  # Check if request was successful

            logging.debug(f"Received response with status code: {response.status_code}")

            # Parse the HTML content returned by Scraper API
            soup = BeautifulSoup(response.content, 'html.parser')

            # Parsing logic to extract data from the page
            data = []
            table = soup.find('table', {'class': 'tableagmark_new'})
            if table:
                headers = [translate_header(header.text.strip()) for header in table.find_all('th')]
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    cols = [col.text.strip() for col in cols]
                    if 'No Data Found' in cols:
                        data = None
                        break
                    data.append(dict(zip(headers, cols)))
            else:
                data = None

        except requests.exceptions.Timeout:
            logging.error("The request timed out.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during request: {e}")

    return render_template('index.html', data=data, form_submitted=form_submitted)

if __name__ == '__main__':
    app.run(debug=True)
