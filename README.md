# Off the Heat

A heat-safe shift planner: an Android app that tells a construction-site supervisor which hours are safe for outdoor work in extreme heat, and turns the plan into a Hindi voice note for the crew.

Team OpusCube's entry for the WeMakeDevs x AWS environmental hackathon, Heat and Water track.

## Try it

- The app in a browser: https://d1gu9h8j3658ef.cloudfront.net
- The Android app: https://d1gu9h8j3658ef.cloudfront.net/download/app.apk (not on the Play Store, so Android shows an unknown-source warning)

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
EventBridge Scheduler --> planner Lambda (risk engine + plan templates)
                                |--> Open-Meteo, Amazon Polly, Amazon S3
```

- The supervisor sets up a site once; the app asks the API for a plan and polls until it is ready.
- The planner fetches the hourly forecast from Open-Meteo and the risk engine scores every shift hour.
- The plan text is built from fixed Hindi and English sentences, filled with the engine's numbers.
- The risk engine is plain, tested Python (NWS heat index plus IMD temperature cut-offs). **No AI model is involved: the same weather always gives the same plan**, and the tests check that every number in the plan text came from the engine.
- Amazon Polly turns the plan into a Hindi voice note to share with the crew.
- On dangerous days the plan carries a fixed heat-stroke warning, checked by the team, shown word for word.

## Built with

AWS SAM CLI (AWS open source), AWS Lambda, Amazon API Gateway, Amazon CloudFront, Amazon Polly, Amazon DynamoDB, Amazon S3 and Amazon EventBridge Scheduler. The app is React, Vite and TypeScript, packaged for Android with Capacitor.

## Run it

Needs Python 3.11+, Node.js, AWS CLI v2, SAM CLI and Docker.

```bash
pip install -r requirements.txt
pytest
```

```bash
sam build
sam deploy
```

```bash
npm --prefix web install
npm --prefix web run build
aws s3 sync web/dist s3://<WebBucketName> --delete --exclude "download/*"
```

`WebBucketName` and the app's link are printed by the deploy.

## Attribution

Weather data by [Open-Meteo](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Heat index from the US National Weather Service (NOAA WPC); temperature cut-offs follow India Meteorological Department heatwave criteria.
