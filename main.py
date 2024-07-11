import csv
import requests
import json


company_search_url = "https://sandbox.aadhaarkyc.io/api/v1/corporate/name-to-cin-list"

Company_cin_url = "https://sandbox.aadhaarkyc.io/api/v1/corporate/company-details"

director_phone_number_url = "https://sandbox.surepass.io/api/v1/corporate/director-phone"

director_email_url = "https://sandbox.surepass.io/api/v1/corporate/din"

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer YOUR TOKEN'
}

input_file = "input_file.csv"
output_file = "output_file.csv"

with open(output_file, 'a', encoding='latin-1', newline='') as write_csv:
  csv_write = csv.DictWriter(write_csv, fieldnames=['company_name', 'name', 'email_id', 'phone_number'])
  if write_csv.tell() == 0:
    csv_write.writeheader()

  with open(input_file, 'r', encoding='latin-1') as read_csv:
    csv_read = csv.DictReader(read_csv)
    for csv_company in csv_read:
      company = csv_company.get('company')

      company_search_payload = json.dumps({
        "company_name_search": company
      })
      company_search_response = requests.request("POST", company_search_url, headers=headers,
                                                 data=company_search_payload)

      if company_search_response.status_code == 200:
        company_response = company_search_response.json()
        company_cin_list = company_response['data']['company_list']
        for cin_info in company_cin_list:
          cin = cin_info['cin_number']

          company_cin_payload = json.dumps({
            "id_number": cin
          })

          company_cin_response = requests.request("POST", Company_cin_url, headers=headers, data=company_cin_payload)
          if company_cin_response.status_code == 200:
            company_cin_res = company_cin_response.json()
            company_owner_din_list = company_cin_res['data']['details']['directors']
            for owner in company_owner_din_list:
              director_din = owner['din_number']

              director_phone_number_payload = json.dumps({
                "id_number": director_din
              })

              company_director_res = requests.request("POST", director_phone_number_url, headers=headers,
                                                      data=director_phone_number_payload)
              if company_director_res.status_code == 200:
                company_director_res_ = company_director_res.json()
              else:
                company_director_res_ = {'data': {'phone_number': 'Not available'}}

              company_director_email_res = requests.request("POST", director_email_url, headers=headers,
                                                            data=director_phone_number_payload)
              if company_director_email_res.status_code == 200:
                company_director_email_res_ = company_director_email_res.json()
              else:
                company_director_email_res_ = {'data': {'full_name': 'Not available', 'email': 'Not available'}}

              director_name = company_director_email_res_['data'].get('full_name', 'Not available')
              director_email_id = company_director_email_res_['data'].get('email', 'Not available')
              director_phone_number = company_director_res_['data'].get('phone_number', 'Not available')

              details = {
                'company_name': company,
                'name': director_name,
                'email_id': director_email_id,
                'phone_number': director_phone_number
              }
              csv_write.writerow(details)
          else:
            csv_write.writerow({'company_name': company, 'name': 'Not available', 'email_id': 'Not available',
                                'phone_number': 'Not available'})
      else:
        csv_write.writerow({'company_name': company, 'name': 'Not available', 'email_id': 'Not available',
                            'phone_number': 'Not available'})

