import requests as re

SMTP_SERVER_API_URL = 'https://api.sendgrid.com/v3/mail/send'
API_KEY = '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'
payload = {
    "personalizations": [
        {
            "to": [
                {
                "email": "fellipedfernandes@gmail.com"
                }
            ],
            "dynamic_template_data":
                {
                    "scraperName":"FARM-RIO",
                    "subject":"Scraper run completed!"
                }
        }
    ],

    "from": {
        "email": "fellipe.fernandes@bixtecnologia.com.br",
        "name": "Scraper Notifier Service"
    },

    "template_id":"d-496ec366d67240aebf06186151643716"
    }

header = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + str(API_KEY)
        }


r = re.post(SMTP_SERVER_API_URL, json=payload, headers=header)
print(r.text)