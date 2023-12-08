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

combined_clip_duration = 3  # Durée de la première interaction
user_clip_duration = 2.5  # Durée de chaque clip utilisateur
chatgpt_clip_duration = 3  # Durée de chaque clip de réponse de ChatGPT

# Informations sur le profil de ChatGPT
chatgpt_profile_image_path = "./chatgpt_logo.png"
chatgpt_name = "ChatGPT"

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

def create_user_prompt_clip(prompt, is_combined=False):
    clip_duration = combined_clip_duration if is_combined else user_clip_duration

    padding = 60
    max_width = video_width - 2 * padding
    line_height = 50  # Hauteur d'une ligne de texte

    # Créer les clips pour la photo de profil et le nom d'utilisateur
    profile_pic_clip = ImageClip(user_profile_image_path).set_duration(clip_duration).resize(width=60)
    name_clip = TextClip(user_name, fontsize=35, color='white', font='Arial-Bold').set_duration(clip_duration)

    # Positionner la photo de profil et le nom d'utilisateur
    profile_pic_clip = profile_pic_clip.set_position((padding - 5, 'center'))
    name_clip = name_clip.set_position((padding + 80, 'center'))  # 80 est la largeur de l'image + un petit espace

    # Diviser le prompt en plusieurs lignes et créer des clips de texte pour chaque ligne
    wrapped_prompt = wrap(prompt, width=60)  # Ajustez le paramètre 'width' selon vos besoins
    prompt_clips = []
    y_position = 0  # Position Y initiale pour le premier prompt

    for line in wrapped_prompt:
        line_clip = TextClip(line, fontsize=35, color='white', align='West', size=(max_width, line_height)).set_duration(clip_duration)
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

    # Assembler les clips utilisateur et prompt en un seul
    combined_clip = CompositeVideoClip([user_info_clip, prompt_combined_clip.set_position(('center', user_info_height))], size=(video_width, user_info_height + prompt_height))
    if not is_combined:
        # Étendre à toute la hauteur de la vidéo si utilisé seul
        combined_clip = combined_clip.on_color(color=background_color, col_opacity=1, size=(video_width, video_height))
    return combined_clip


def create_chatgpt_response_clip(image_filename, is_combined=False):
    clip_duration = combined_clip_duration if is_combined else chatgpt_clip_duration

    padding = 60
    profile_pic_width = 60
    element_spacing = 20

    # Clips pour la photo de profil et le nom de ChatGPT
    chatgpt_profile_pic_clip = ImageClip(chatgpt_profile_image_path).set_duration(clip_duration).resize(width=profile_pic_width)
    chatgpt_name_clip = TextClip(chatgpt_name, fontsize=35, color='white', font='Arial-Bold').set_duration(clip_duration)
    chatgpt_name_clip = chatgpt_name_clip.set_position((padding + profile_pic_width + element_spacing, 'center'))

    # Clip pour l'image générée
    generated_image_clip = ImageClip(image_filename).set_duration(clip_duration).resize(width=video_width, height=video_width)

    # Calcul de la position de départ verticale
    user_info_height = max(chatgpt_profile_pic_clip.h, chatgpt_name_clip.h)
    total_response_height = user_info_height + element_spacing + video_width
    start_y_position = 0

    # Positionnement des éléments
    chatgpt_profile_pic_clip = chatgpt_profile_pic_clip.set_position((padding, start_y_position))
    chatgpt_name_clip = chatgpt_name_clip.set_position((padding + profile_pic_width + element_spacing, start_y_position))
    generated_image_clip = generated_image_clip.set_position(('center', start_y_position + user_info_height + element_spacing))

    # Assemblage des clips
    combined_clip = CompositeVideoClip([chatgpt_profile_pic_clip, chatgpt_name_clip, generated_image_clip], size=(video_width, total_response_height))
    if not is_combined:
        combined_clip = combined_clip.on_color(color=background_color, col_opacity=1, size=(video_width, video_height))

    return combined_clip


def create_combined_first_clip(user_prompt, chatgpt_image_filename):
    user_prompt_clip = create_user_prompt_clip(user_prompt, is_combined=True)
    chatgpt_response_clip = create_chatgpt_response_clip(chatgpt_image_filename, is_combined=True)

    # Définir un espace (padding) entre les deux clips
    padding_between_clips = 100  # Ajustez cette valeur selon vos besoins

    # Hauteur totale nécessaire pour les deux clips avec padding
    total_clip_height = user_prompt_clip.h + chatgpt_response_clip.h + padding_between_clips

    # Si la hauteur totale dépasse la hauteur de la vidéo, ajuster la taille de l'image générée
    if total_clip_height > video_height:
        excess_height = total_clip_height - video_height
        new_image_height = video_width - excess_height  # Réduire la hauteur de l'image générée
        chatgpt_response_clip = create_chatgpt_response_clip(chatgpt_image_filename, is_combined=True, new_image_height=new_image_height)

        # Recalculer la hauteur totale après ajustement
        total_clip_height = user_prompt_clip.h + chatgpt_response_clip.h + padding_between_clips

    # Position de départ verticale pour centrer le clip combiné
    start_y_position = (video_height - total_clip_height) // 2

    # Assembler les clips en un seul
    combined_clip = CompositeVideoClip([
        user_prompt_clip.set_position(('center', start_y_position)),
        chatgpt_response_clip.set_position(('center', start_y_position + user_prompt_clip.h + padding_between_clips))
    ], size=(video_width, video_height))
    combined_clip = combined_clip.on_color(color=background_color, col_opacity=1)

    return combined_clip


def create_video_from_json(json_data):
    clips = []

    # Créer un clip spécial pour la première interaction
    if json_data:
        first_user_prompt = json_data[0]['prompt']
        first_chatgpt_image = f"temp_image_0.webp"
        download_image(json_data[0]['imageUrl'], first_chatgpt_image)
        first_combined_clip = create_combined_first_clip(first_user_prompt, first_chatgpt_image)
        clips.append(first_combined_clip)

    # Créer des clips séparés pour les interactions suivantes
    for index, entry in enumerate(json_data[1:], start=1):
        user_prompt_clip = create_user_prompt_clip(entry['prompt'])
        image_filename = f"temp_image_{index}.webp"
        download_image(entry['imageUrl'], image_filename)
        chatgpt_response_clip = create_chatgpt_response_clip(image_filename)
        clips.extend([user_prompt_clip, chatgpt_response_clip])

    # Concaténer tous les clips dans la vidéo finale
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile("output.mp4", fps=24)

    # Nettoyer les fichiers image temporaires
    for index in range(len(json_data)):
        os.remove(f"temp_image_{index}.webp")

if __name__ == "__main__":
    json_data = json.loads(sys.argv[1])
    create_video_from_json(json_data)