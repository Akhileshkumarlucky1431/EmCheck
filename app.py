import os
import sys
from pathlib import Path
from typing import Optional
import anthropic
from openai import OpenAI
from google.cloud import texttospeech
import subprocess
import json

class AnimationVideoCreator:
    def __init__(self):
        self.client_anthropic = anthropic.Anthropic()
        self.client_openai = OpenAI()
        self.tts_client = texttospeech.TextToSpeechClient()
        self.output_dir = Path("generated_videos")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_script_from_prompt(self, prompt: str) -> str:
        """Generate a script in Hindi from user prompt using Claude."""
        try:
            message = self.client_anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a Hindi script writer for educational animations. 
                        Create a concise, engaging Hindi script (150-200 words) based on this prompt: {prompt}
                        
                        Format the response as:
                        TITLE: [Hindi title]
                        SCRIPT: [Hindi script]
                        TONE: [educational/fun/motivational]
                        
                        Make it suitable for students and educational content."""
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error generating script: {e}")
            return None
    
    def generate_indian_face_description(self, character_type: str = "student") -> str:
        """Generate description of Indian face for animation using DALL-E."""
        try:
            response = self.client_openai.images.generate(
                model="dall-e-3",
                prompt=f"Generate a professional illustration of a {character_type} with Indian features, 3D animated style, friendly expression, suitable for educational video",
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        except Exception as e:
            print(f"Error generating face: {e}")
            return None
    
    def convert_text_to_speech_hindi(self, text: str, output_path: str) -> bool:
        """Convert Hindi text to speech using Google Cloud TTS."""
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code="hi-IN",
                name="hi-IN-Neural2-A",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            print(f"Audio saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error converting text to speech: {e}")
            return False
    
    def create_animation_video(self, prompt: str, video_name: Optional[str] = None) -> Optional[str]:
        """Create animation video from simple prompt."""
        print(f"\n🎬 Creating animation from prompt: {prompt}\n")
        
        # Step 1: Generate script
        print("📝 Step 1: Generating Hindi script...")
        script_response = self.generate_script_from_prompt(prompt)
        if not script_response:
            return None
        print(f"✅ Script generated:\n{script_response}\n")
        
        # Step 2: Generate face/character
        print("🎨 Step 2: Generating Indian character...")
        face_url = self.generate_indian_face_description()
        if face_url:
            print(f"✅ Character generated: {face_url}\n")
        
        # Step 3: Extract Hindi text from script
        try:
            script_text = script_response.split("SCRIPT: ")[1].split("\nTONE:")[0]
        except:
            script_text = script_response
        
        # Step 4: Generate audio
        print("🔊 Step 3: Generating Hindi audio...")
        audio_path = self.output_dir / f"audio_{video_name or 'default'}.mp3"
        if self.convert_text_to_speech_hindi(script_text, str(audio_path)):
            print(f"✅ Audio generated: {audio_path}\n")
        
        # Step 5: Create video (placeholder for actual video generation)
        print("🎬 Step 4: Creating video...")
        video_path = self.output_dir / f"video_{video_name or 'default'}.mp4"
        
        # Using FFmpeg to create a simple video
        try:
            subprocess.run([
                "ffmpeg", "-loop", "1", "-i", "placeholder.png",
                "-i", str(audio_path), "-c:v", "libx264", "-c:a", "aac",
                "-shortest", str(video_path)
            ], check=True)
            print(f"✅ Video created: {video_path}\n")
            return str(video_path)
        except Exception as e:
            print(f"⚠️ Video generation needs FFmpeg: {e}")
            return str(audio_path)
    
    def create_from_simple_prompt(self, prompt: str) -> None:
        """Simple interface to create video from one-line prompt."""
        video_path = self.create_animation_video(prompt)
        if video_path:
            print(f"🎉 Animation created successfully!")
            print(f"📁 Output: {video_path}")
        else:
            print("❌ Failed to create animation")


def main():
    creator = AnimationVideoCreator()
    
    # Example prompts
    examples = [
        "Create a video about how photosynthesis works for Class 10 students",
        "Make an animated story about the importance of water conservation in Hindi",
        "Generate a tutorial video about basic math fractions for kids"
    ]
    
    print("🎬 AI Animation Video Creator with Simple Prompts")
    print("=" * 50)
    print("\nExample prompts:")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print("\n" + "=" * 50)
    user_prompt = input("\n📝 Enter your prompt (or press Enter for example 1): ").strip()
    
    if not user_prompt:
        user_prompt = examples[0]
    
    creator.create_from_simple_prompt(user_prompt)


if __name__ == "__main__":
    main()