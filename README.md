# Heat-safe shift planner (name TBD)

An Android app that tells a construction-site supervisor which hours are safe for outdoor work in extreme heat, and turns the plan into a Hindi voice note for the crew.

Team OpusCube's entry for the WeMakeDevs x AWS environmental hackathon, Heat and Water track.

## The problem

Outdoor workers in Rajasthan keep working through dangerous afternoon heat because nobody turns the weather forecast into a shift decision. One supervisor sets the hours for a whole crew, so the app is built for that person. Workers get the plan as a voice note on WhatsApp: no app, no reading.

## How it works

```
Android app and web link (one React codebase)
        |
Amazon CloudFront
        |-- app files --> Amazon S3
        |-- /api/* ----> API Gateway + api Lambda --> Amazon DynamoDB
                                |  async
                                v
EventBridge Scheduler --> planner Lambda (Strands agent + risk engine)
                                |--> Open-Meteo, Amazon Bedrock, Amazon Polly, Amazon S3
```

- The supervisor sets up a site once; the app asks the API for a plan and polls until it is ready.
- A Strands agent on Amazon Bedrock fetches the hourly forecast and passes it to the risk engine.
- The risk engine is plain, tested Python (NWS heat index plus IMD temperature cut-offs). **The model never decides a band, a temperature or a time; it only words what the engine returns**, and a guard rejects any number the engine did not produce.
- Amazon Polly turns the plan into a Hindi voice note to share with the crew.
- On dangerous days the plan carries a fixed, human-written heat-stroke warning that never passes through the model.

## Built with

Strands Agents SDK and AWS SAM CLI (both AWS open source), AWS Lambda, Amazon API Gateway, Amazon CloudFront, Amazon Bedrock (Claude Haiku), Amazon Polly, Amazon DynamoDB, Amazon S3 and Amazon EventBridge Scheduler. The app is React, Vite and TypeScript, packaged for Android with Capacitor.

## Run it

Needs Python 3.11+, Node.js, AWS CLI v2, SAM CLI, Docker, and Bedrock access to Claude Haiku in `us-east-1`.

```bash
pip install -r requirements.txt
pytest
```

```bash
sam build
sam deploy --parameter-overrides BedrockModelId=<Claude Haiku model or inference profile ID>
```

```bash
npm --prefix web install
npm --prefix web run build
aws s3 sync web/dist s3://<WebBucketName> --delete --exclude "download/*"
```

`WebBucketName` and the app's link are printed by the deploy.

## Attribution

Weather data by [Open-Meteo](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Heat index from the US National Weather Service (NOAA WPC); temperature cut-offs follow India Meteorological Department heatwave criteria.
