import requests
# import numpy as np
import time
import json

from config import service_region, subscription_key, source_files, results_blob

# Cognitive Services endpoint
endpoint = f"https://{service_region}.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions"

###########################################################

### Call API to initiate batch transcription 

print("Calling API to transcribe file...")

# Setup call parameters
headers = {
    'Ocp-Apim-Subscription-Key': subscription_key,
    'Content-Type':'application/json'
}

data = {
    'contentURLs':source_files,
    'destinationContainerUrl':results_blob,
    'locale':"en-US",
    'displayName':"My Transcription",
#    'model':np.NaN,
    'properties':{
        "wordLevelTimestampsEnabled": True,
#         'diarization':'true',
         "diarizationEnabled":True,
         "languageIdentification": {
          "candidateLocales": [
            "en-US", "de-DE", "es-ES"
          ],
        }
    }
}

# Make POST call to cog services API
res = requests.post(endpoint, headers=headers, data=json.dumps(data))

## Monitor batch transcription jobs until they are complete 
print("Monitoring for transcription job completion...")
status = {}; status["values"] = []

while status["values"] == []:
    print("Not complete yet. Waiting...")
    time.sleep(5)
    res_file = requests.get(res.json()["links"]["files"],
                            headers={"Ocp-Apim-Subscription-Key":subscription_key})
    status = json.loads(res_file.text)
print("Transcriptions complete!")

## Gather transcription job results
print("Collecting transcription results...")

transcriptions = []
treports = []
for z in status["values"]:
    url = z["links"]["contentUrl"]
    res_final = requests.get(url,
                            headers={"Ocp-Apim-Subscription-Key":subscription_key})
    kind = z["kind"]
    print(f'Processing report of type: {kind}')
    if kind == "Transcription":
        transcriptions.append(res_final.json())
    elif kind == "TranscriptionReport":
        treports.append(res_final.json())
        print(res_final.text)
    else:
        print("Unknown report type found!")
