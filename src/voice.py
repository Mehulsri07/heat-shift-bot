"""Crew voice note: Polly speech saved to S3 as MP3."""
import os
import uuid

import boto3


def make_voice_note(text: str, language: str) -> str:
    """Speak `text` with Polly and return the S3 key of the MP3."""
    speech = boto3.client("polly").synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        Engine="neural",
        VoiceId=os.environ["POLLY_VOICE_ID"],
        # hi-IN makes Polly read numbers in Hindi.
        LanguageCode="hi-IN" if language == "hi" else "en-IN",
    )
    key = f"voice/{uuid.uuid4()}.mp3"
    boto3.client("s3").put_object(
        Bucket=os.environ["AUDIO_BUCKET"],
        Key=key,
        Body=speech["AudioStream"].read(),
        ContentType="audio/mpeg",
    )
    return key
