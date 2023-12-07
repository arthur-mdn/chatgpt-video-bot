from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip
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
user_name = "@ia_generation_ai"

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
    # Marge appliquée autour des éléments
    padding = 60

    # Créer un clip pour la photo de profil
    profile_pic_clip = ImageClip(user_profile_image_path, transparent=True).set_duration(1).resize(width=50)

    # Créer un clip pour le nom d'utilisateur
    name_clip = TextClip(user_name, fontsize=30, color='white').set_duration(1)

    # Positionner la photo de profil et le nom d'utilisateur
    profile_pic_clip = profile_pic_clip.set_position((padding, 'center'))
    name_clip = name_clip.set_position((padding + 80, 'center'))  # 80 est la largeur de l'image + un petit espace

    # Position X de départ pour le prompt (aligné avec le nom d'utilisateur)
    prompt_start_x = padding + 80

    # Créer un clip pour le prompt
    #prompt_clip = TextClip(prompt, fontsize=30, color='white', size=(video_width - prompt_start_x - padding, video_height // 10)).set_duration(1)
    #prompt_clip = prompt_clip.set_position((prompt_start_x, 'center')).on_color(color=(255, 0, 0), col_opacity=0.5)
    prompt_clip = TextClip(prompt, fontsize=30, color='white').set_duration(1)
    prompt_clip = prompt_clip.set_position((prompt_start_x + 80, 'center')).on_color(color=(255, 0, 0), col_opacity=0.5)

    # Assembler la photo de profil et le nom d'utilisateur dans un seul clip
    user_info_clip = CompositeVideoClip([profile_pic_clip, name_clip], size=(video_width, 50))
    user_info_clip = user_info_clip.set_position(('center', 'top'))

    # Appliquer la couleur de fond à l'ensemble du clip utilisateur
    user_clip_background = CompositeVideoClip([user_info_clip, prompt_clip], size=(video_width, video_height // 5)).set_position('top')
    user_clip_background = user_clip_background.on_color(color=background_color, col_opacity=1, size=(video_width, video_height))

    return user_clip_background



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
