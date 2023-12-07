from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip
from textwrap import wrap
import requests
import os
import sys
import json

# Define the size of the video
video_width = 1080
video_height = 1920

# Define background color
background_color = (52, 53, 65)

# User profile information
user_profile_image_path = "./profile_picture.png"
user_name = "ia_generation_ai"

def download_image(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'image/webp,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(f"Erreur lors du téléchargement de l'image: {response.status_code}")

def create_user_prompt_clip(prompt):
    padding = 60
    max_width = video_width - 2 * padding
    line_height = 50  # Hauteur d'une ligne de texte

    # Créer les clips pour la photo de profil et le nom d'utilisateur
    profile_pic_clip = ImageClip(user_profile_image_path, transparent=True).set_duration(3).resize(width=60)
    name_clip = TextClip(user_name, fontsize=30, color='white', font='Arial-Bold').set_duration(3)

    # Positionner la photo de profil et le nom d'utilisateur
    profile_pic_clip = profile_pic_clip.set_position((padding - 5, 'center'))
    name_clip = name_clip.set_position((padding + 80, 'center'))  # 80 est la largeur de l'image + un petit espace

    # Diviser le prompt en plusieurs lignes et créer des clips de texte pour chaque ligne
    wrapped_prompt = wrap(prompt, width=60)  # Ajustez le paramètre 'width' selon vos besoins
    prompt_clips = []
    y_position = 0  # Position Y initiale pour le premier prompt

    for line in wrapped_prompt:
        line_clip = TextClip(line, fontsize=30, color='white', align='West', size=(max_width, line_height)).set_duration(3)
        line_clip = line_clip.set_position((padding, y_position))
        prompt_clips.append(line_clip)
        y_position += line_height  # Ajouter un espace entre les lignes

    # Assembler les clips de prompt dans un seul clip
    prompt_combined_clip = CompositeVideoClip(prompt_clips, size=(max_width, y_position))
    prompt_height = y_position  # Hauteur totale du prompt

    # Assembler la photo de profil et le nom d'utilisateur dans un seul clip
    user_info_height = 120  # Hauteur ajustée pour l'ensemble de l'info utilisateur
    user_info_clip = CompositeVideoClip([profile_pic_clip, name_clip], size=(video_width, user_info_height))
    user_info_clip = user_info_clip.set_position(('center', 'top'))

    # Positionner le prompt sous les infos utilisateur
    prompt_combined_clip = prompt_combined_clip.set_position(('center', user_info_height))

    # Combinaison finale du clip d'information de l'utilisateur et du prompt
    combined_clip = CompositeVideoClip([user_info_clip, prompt_combined_clip], size=(video_width, user_info_height + prompt_height))
    combined_clip = combined_clip.on_color(color=background_color, col_opacity=1, size=(video_width, video_height))

    return combined_clip





def create_video_from_json(json_data):
    clips = []

    for index, entry in enumerate(json_data):
        # Create a clip for the user prompt
        user_prompt_clip = create_user_prompt_clip(entry['prompt'])

        # Download and create a clip for the image
        image_filename = f"temp_image_{index}.webp"
        download_image(entry['imageUrl'], image_filename)
        image_clip = ImageClip(image_filename).set_duration(1)

        # Resize the image to fit the video dimensions
        image_clip = image_clip.resize(height=video_height // 2)

        # Create a text clip for the response
        response_clip = TextClip(entry['response'], fontsize=30, color='white', size=(video_width, video_height // 10))
        response_clip = response_clip.set_duration(1).set_position("center").on_color(color=background_color, col_opacity=1)

        # Combine the image and response text into one clip
        combined_clip = CompositeVideoClip([image_clip.set_position("top"), response_clip.set_position("bottom")], size=(video_width, video_height))

        # Apply the background color to the entire clip
        combined_clip = combined_clip.on_color(color=background_color, col_opacity=1)

        # Add the clips to the final video
        clips.extend([user_prompt_clip, combined_clip])

    # Concatenate all the clips into the final video
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile("output.mp4", fps=24)

    # Clean up the temporary image files
    for index in range(len(json_data)):
        os.remove(f"temp_image_{index}.webp")

if __name__ == "__main__":
    json_data = json.loads(sys.argv[1])
    create_video_from_json(json_data)
