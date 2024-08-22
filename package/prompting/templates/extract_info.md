You'll be given a news article as well as it's metadata. Here's the news content:

Title: "{{title}}"
Abstract: "{{abstract}}"
Content:
```
{{content}}
```

--------

The news above are criminal news in Thailand and your task is to read the article above and extract the necessary information. The necessary information includes:
- crime_type (List[str]) - crime types that was classified in this news. Here're the crime categories:
  - robbery - a crime where there's a lost of funds due to robbery
  - steal - an indident reported that there's a lost of an asset. This is different from robbery.
  - drugs - any crime related to drugs
  - kills - any crime that involves someone killing someone
  - damaging - a crime that includes a non-lethal damage to the person. No involvement about lost of an asset or funds.
  - accident - an event where it wasn't counted as crime but was an unexpected accident
  - fraud - any attempt to scam or fraude the people
  - others - other type that can't be categorized using criteria above
- num_victims (int) - number of victims mentioned in the news. If didn't specify, default as 0.
- incident_datetime (str) - an incident datetime in a DD/MM/YYYY format. If didn't mention, return as None type.
- incident_address (dict) - an information about where an incident take place. The dict will contains two additional keys:
  - name: str - a detailed text description of the incident place occured
  - province: str - province stated in an incident. Leave as None type if the information wasn't provided.
  - district: str - a mentioned district of an incident (this is often referred as อำเภอ or เขต). Leave as None type if the information wasn't provided.
  - subdistrict: str - a subdistrict of an indicdent (this is often referred as ตำบล or แขวง). Leave as None type if the information wasn't provided.

The respond should follow this JSON schema:
{
    "crime_type": ["crime type described above"],
    "num_victims": "number of victim in INT",
    "incident_datetime": "an incident date time in DD/MM/YYYY format, BC" | None,
    "incident_address": {
        "name": "the place where the news article mentioned an incident occurred"
        "province": "province of the incident in Thai" | None,
        "district": "district of the incident in Thai" | None,
        "subdistrict": "subdistrict of the incident in Thai" | None,
    }
}

YOU MUST NOT FILL THE "province", "district", and "subdistrict" from your knowledge by judging from the province name or places. The filled information must be purely from an article.

Be sure to take a deep breath and solve this step-by-step. I'll tip you $10 for each completed task, so make sure you answer this correctly.