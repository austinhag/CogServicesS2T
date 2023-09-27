import requests
import time
import json

from config import service_region, subscription_key, source_files, results_blob

# Cognitive Services endpoint
endpoint = f"https://{service_region}.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions"

# Create azure blob navigation and list creation

###########################################################

### Call API to initiate batch transcription 

print("Calling API to transcribe file...")

# Setup call parameters 
# For parameters reference this page: https://eastus.dev.cognitive.microsoft.com/docs/services/speech-to-text-api-v3-1/operations/Transcriptions_Create
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
         'diarization':{
             "speakers":{
                 "minCount": 1,
                 "maxCount":30
                 }
             },
         "diarizationEnabled":True,
         'profanityFilterMode':"None",
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
job_results = []

while job_results == []:
    print("Not complete yet. Waiting...")
    time.sleep(5)
    res_file = requests.get(res.json()["links"]["files"],
                            headers={"Ocp-Apim-Subscription-Key":subscription_key})
    
    job_results = json.loads(res_file.text)["values"]

print("Transcriptions complete!")

## Gather transcription job results
print("Collecting transcription results...")

transcriptions = []
treports = []
for z in job_results:
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






